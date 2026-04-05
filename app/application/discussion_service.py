"""Discussion turns: submit user, run next, auto-run, status."""

from __future__ import annotations

from pathlib import Path

from app.application.config import AppConfig
from app.integration_logging import warn_optional_hook_failed
from app.application.exceptions import PhaseConflictError, SessionNotFoundError
from app.runtime.enums import RoleType
from app.runtime.execution.discussion_loop import auto_run_discussion
from app.runtime.execution.turn_executor import TurnExecutor
from app.runtime.orchestrator.state_machine import SessionStateMachine
from app.runtime.profile_resolver import resolve_runtime_profile
from app.runtime.retrieval.index_loader import has_indexes
from app.runtime.retrieval.router import RoleRouter, build_repositories
from app.runtime.schemas.agent import AgentReply
from app.runtime.schemas.session import SessionContext
from app.runtime.snapshot_loader import load_snapshot

from .audio_service import AudioService
from .mode_service import ModeService
from .session_service import SessionService

class DiscussionService:
    def __init__(self, config: AppConfig, session_service: SessionService) -> None:
        self._config = config
        self._sessions = session_service
        self._audio = AudioService(config, session_service)

    def _mode(self) -> ModeService:
        return ModeService(self._config, self._sessions)

    def _executor(self, ctx: SessionContext) -> TurnExecutor:
        if not ctx.snapshot_dir:
            raise SessionNotFoundError("session missing snapshot_dir")
        return TurnExecutor.from_paths(Path(ctx.snapshot_dir), ctx)

    def submit_user_turn(self, session_id: str, text: str) -> SessionContext:
        ctx = self._sessions.manager.load(session_id)
        if not ctx:
            raise SessionNotFoundError(session_id)
        if ctx.phase == "feedback":
            raise PhaseConflictError("Cannot add user turn in feedback phase")
        ex = self._executor(ctx)
        ex.submit_user_turn(text)
        self._sessions.manager.save(ex.session)
        try:
            self._mode().on_user_turn_committed(session_id, text)
        except Exception as exc:
            warn_optional_hook_failed("mode.on_user_turn_committed", exc, session_id=session_id)
        return ex.session

    def run_next_turn(
        self,
        session_id: str,
        *,
        with_tts: bool = False,
        tts_provider: str | None = None,
    ) -> tuple[SessionContext, AgentReply | None, str]:
        ctx = self._sessions.manager.load(session_id)
        if not ctx:
            raise SessionNotFoundError(session_id)
        if ctx.phase == "feedback":
            raise PhaseConflictError("Discussion already in feedback phase")
        ex = self._executor(ctx)
        sess, reply = ex.run_next_turn()
        self._sessions.manager.save(sess)
        try:
            self._mode().on_turn_saved(session_id)
        except Exception as exc:
            warn_optional_hook_failed("mode.on_turn_saved", exc, session_id=session_id)
        if (
            with_tts
            and self._config.enable_audio
            and reply is not None
            and sess.turns
            and sess.turns[-1].speaker_role != RoleType.USER.value
        ):
            last = sess.turns[-1]
            self._audio.synthesize_turn_audio(session_id, last.turn_id, provider_name=tts_provider)
            sess = self._sessions.manager.load(session_id) or sess
        last = sess.turns[-1].speaker_role if sess.turns else None
        next_up = ex.sm.peek_next_role(sess, last)
        return sess, reply, next_up

    def auto_run_discussion(
        self, session_id: str, *, max_steps: int, auto_fill_user: bool = True
    ) -> tuple[SessionContext, list[AgentReply]]:
        ctx = self._sessions.manager.load(session_id)
        if not ctx:
            raise SessionNotFoundError(session_id)
        if ctx.phase == "feedback":
            raise PhaseConflictError("Cannot auto-run in feedback phase")
        ex = self._executor(ctx)
        sess, replies = auto_run_discussion(ex, max_steps=max_steps, auto_fill_user=auto_fill_user)
        self._sessions.manager.save(sess)
        try:
            self._mode().on_turn_saved(session_id)
        except Exception as exc:
            warn_optional_hook_failed("mode.on_turn_saved", exc, session_id=session_id)
        return sess, replies

    def get_session_status(self, session_id: str) -> dict:
        ctx = self._sessions.get_session(session_id)
        last = ctx.turns[-1].speaker_role if ctx.turns else None
        sm = None
        if ctx.snapshot_dir:
            try:
                bundle = load_snapshot(Path(ctx.snapshot_dir))
                ped, top, ev, doc, _src = build_repositories(bundle)
                sm = SessionStateMachine(RoleRouter(ped, top, ev, doc, snapshot_dir=bundle.path))
            except OSError:
                sm = None
        can_run = ctx.phase != "feedback" and bool(ctx.snapshot_dir)
        next_hint = None
        if self._config.enable_group_sim and ctx.participants:
            try:
                from app.group_sim.engines.turn_allocator import allocate_next_speaker

                plan = allocate_next_speaker(ctx, last)
                if plan:
                    next_hint = plan.next_role
            except Exception as exc:
                warn_optional_hook_failed("group_sim.allocate_next_speaker", exc, session_id=session_id)
                next_hint = None
        if next_hint is None and sm and can_run:
            next_hint = sm.peek_next_role(ctx, last)
        feedback_ready = len(ctx.turns) > 0
        coach_preview = None
        if ctx.coach_report and isinstance(ctx.coach_report, dict):
            txt = str(ctx.coach_report.get("text") or "")
            coach_preview = txt[:1200] if txt else None
        prof = resolve_runtime_profile(ctx.runtime_profile_id)
        rmode = str((prof.retrieval or {}).get("mode", "rule"))
        has_idx = bool(ctx.snapshot_dir and has_indexes(Path(ctx.snapshot_dir)))
        mode_block: dict = {}
        if self._config.enable_practice_modes:
            try:
                mode_block = self._mode().get_mode_status(session_id)
            except Exception as exc:
                warn_optional_hook_failed("mode.get_mode_status", exc, session_id=session_id)
                mode_block = {}
        return {
            "session_id": ctx.session_id,
            "topic_id": ctx.topic_id,
            "learner_id": ctx.learner_id,
            "mode_id": ctx.mode_id,
            "preset_id": ctx.preset_id,
            "drill_id": ctx.drill_id,
            "assessment_template_id": ctx.assessment_template_id,
            "mode_report_id": ctx.mode_report_id,
            "mode_state": ctx.mode_state,
            "timer_state": mode_block.get("timer_state") if mode_block else ctx.timer_state,
            "simulation_note": mode_block.get("simulation_note"),
            "phase": ctx.phase,
            "runtime_profile_id": ctx.runtime_profile_id,
            "retrieval_mode": rmode,
            "has_indexes": has_idx,
            "provider_name": ctx.provider_name,
            "model_name": ctx.model_name,
            "turn_count": len(ctx.turns),
            "latest_turns": [t.model_dump() for t in ctx.turns],
            "feedback_ready": feedback_ready,
            "coach_report_present": ctx.coach_report is not None,
            "coach_text_preview": coach_preview,
            "can_run_next": bool(
                can_run and next_hint is not None and next_hint != RoleType.USER.value
            ),
            "peek_next_role": next_hint,
            "audio_enabled": bool(ctx.audio_enabled),
            "asr_provider_name": ctx.asr_provider_name,
            "tts_provider_name": ctx.tts_provider_name,
            "audio_asset_count": len(ctx.audio_asset_ids or []),
            "speech_report_id": ctx.speech_report_id,
            "speech_analysis_enabled": bool(ctx.speech_analysis_enabled),
            "roster_template_id": ctx.roster_template_id,
            "user_participant_id": ctx.user_participant_id,
            "participants": list(ctx.participants or []),
            "teams": list(ctx.teams or []),
            "group_balance_report_id": ctx.group_balance_report_id,
            "next_candidate_participant_ids": ctx.next_candidate_participant_ids or [],
            "curriculum_pack_id": ctx.curriculum_pack_id,
            "assignment_id": ctx.assignment_id,
            "assignment_step_id": ctx.assignment_step_id,
        }
