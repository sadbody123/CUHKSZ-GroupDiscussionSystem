"""Analyzer + coach feedback."""

from __future__ import annotations

import logging
from pathlib import Path

from app.application.audio_service import AudioService
from app.integration_logging import warn_optional_hook_failed
from app.application.config import get_app_config
from app.application.exceptions import SessionNotFoundError
from app.runtime.evaluation.analyzers import analyze_transcript_turns
from app.runtime.evaluation.feedback_packet import build_feedback_packet
from app.audio.analysis.constants import DEFAULT_PROXY_DISCLAIMER
from app.application.speech_analysis_service import SpeechAnalysisService
from app.runtime.execution.feedback_runner import run_generate_feedback
from app.runtime.execution.turn_executor import TurnExecutor
from app.runtime.retrieval.router import build_repositories
from app.runtime.schemas.coach_report import CoachReport
from app.runtime.snapshot_loader import load_snapshot

from .session_service import SessionService

_logger = logging.getLogger(__name__)


class FeedbackService:
    def __init__(self, session_service: SessionService) -> None:
        self._sessions = session_service
        self._audio = AudioService(get_app_config(), session_service)

    def analyze_transcript(self, session_id: str) -> dict:
        ctx = self._sessions.manager.load(session_id)
        if not ctx or not ctx.snapshot_dir:
            raise SessionNotFoundError(session_id)
        b = load_snapshot(Path(ctx.snapshot_dir))
        ped, _top, _ev, _doc, _src = build_repositories(b)
        metrics, sigs = analyze_transcript_turns(ctx.turns)
        fb = build_feedback_packet(
            session_id=ctx.session_id,
            topic_id=ctx.topic_id,
            metrics=metrics,
            detected_signals=sigs,
            pedagogy=ped,
        )
        return fb.model_dump()

    def generate_feedback(
        self,
        session_id: str,
        *,
        with_tts: bool = False,
        tts_provider: str | None = None,
        with_speech_analysis: bool = False,
        speech_profile_id: str | None = None,
    ) -> CoachReport:
        ctx = self._sessions.manager.load(session_id)
        if not ctx or not ctx.snapshot_dir:
            raise SessionNotFoundError(session_id)
        speech_session_report: dict | None = None
        speech_disclaimer: str | None = None
        if with_speech_analysis and get_app_config().enable_speech_analysis:
            try:
                sas = SpeechAnalysisService(get_app_config(), self._sessions)
                speech_session_report = sas.analyze_session_speech(
                    session_id,
                    profile_id=speech_profile_id or ctx.runtime_profile_id,
                )
                speech_disclaimer = (speech_session_report or {}).get("proxy_disclaimer") or DEFAULT_PROXY_DISCLAIMER
            except Exception as exc:
                _logger.warning(
                    "Speech analysis disabled for this feedback run (session_id=%s): %s",
                    session_id,
                    exc,
                )
                speech_session_report = None
                speech_disclaimer = None
        ex = TurnExecutor.from_paths(Path(ctx.snapshot_dir), ctx)
        report = run_generate_feedback(
            ex,
            self._sessions.manager,
            speech_session_report=speech_session_report,
            speech_proxy_disclaimer=speech_disclaimer,
        )
        if with_tts and get_app_config().enable_audio:
            self._audio.synthesize_coach_report_audio(session_id, provider_name=tts_provider)
        try:
            from app.application.learner_service import LearnerService

            LearnerService(get_app_config(), self._sessions).maybe_auto_ingest_after_feedback(session_id)
        except Exception as exc:
            warn_optional_hook_failed("learner.maybe_auto_ingest_after_feedback", exc, session_id=session_id)
        try:
            from app.application.mode_service import ModeService

            ModeService(get_app_config(), self._sessions).maybe_auto_mode_report(session_id)
        except Exception as exc:
            warn_optional_hook_failed("mode.maybe_auto_mode_report", exc, session_id=session_id)
        try:
            from app.application.group_service import GroupService

            GroupService(get_app_config(), self._sessions).maybe_auto_group_report(session_id)
        except Exception as exc:
            warn_optional_hook_failed("group.maybe_auto_group_report", exc, session_id=session_id)
        try:
            cfg = get_app_config()
            if getattr(cfg, "auto_create_review_pack_after_feedback", False) and getattr(
                cfg, "enable_review_workspace", True
            ):
                from app.application.review_service import ReviewService

                ReviewService(cfg, self._sessions).create_review_pack(session_id)
        except Exception as exc:
            warn_optional_hook_failed("review.create_review_pack_after_feedback", exc, session_id=session_id)
        try:
            cfg = get_app_config()
            if getattr(cfg, "auto_attach_session_to_assignment", False) and getattr(
                cfg, "enable_curriculum_delivery", True
            ):
                ctx = self._sessions.manager.load(session_id)
                if ctx and ctx.assignment_id and ctx.metadata.get("curriculum_pack_step_id"):
                    from app.application.curriculum_service import CurriculumService

                    CurriculumService(cfg, self._sessions).attach_session_to_assignment_step(
                        assignment_id=ctx.assignment_id,
                        pack_step_id=str(ctx.metadata["curriculum_pack_step_id"]),
                        session_id=session_id,
                    )
        except Exception as exc:
            warn_optional_hook_failed("curriculum.attach_session_to_assignment_step", exc, session_id=session_id)
        return report
