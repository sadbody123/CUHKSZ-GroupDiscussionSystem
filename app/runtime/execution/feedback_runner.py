"""Coach feedback generation from transcript."""

from __future__ import annotations

from typing import Any

from app.runtime.agents.coach_agent import generate_coach_report
from app.runtime.evaluation.analyzers import analyze_transcript_turns
from app.runtime.profile_resolver import resolve_runtime_profile
from app.runtime.evaluation.feedback_packet import build_feedback_packet
from app.runtime.execution.turn_executor import TurnExecutor
from app.runtime.retrieval.router import build_repositories
from app.runtime.schemas.coach_report import CoachReport
from app.runtime.schemas.feedback import FeedbackPacket
from app.runtime.session.manager import SessionManager


def run_generate_feedback(
    executor: TurnExecutor,
    manager: SessionManager,
    *,
    speech_session_report: dict[str, Any] | None = None,
    speech_proxy_disclaimer: str | None = None,
) -> CoachReport:
    session = executor.session
    session.phase = "feedback"
    ped, _, _, _, _ = build_repositories(executor.bundle)
    prof = resolve_runtime_profile(session.runtime_profile_id)
    metrics, sigs = analyze_transcript_turns(session.turns, analyzer_config=dict(prof.analyzer))
    fb = build_feedback_packet(
        session_id=session.session_id,
        topic_id=session.topic_id,
        metrics=metrics,
        detected_signals=sigs,
        pedagogy=ped,
    )
    fb = _merge_speech_feedback(
        fb,
        speech_session_report=speech_session_report,
        speech_proxy_disclaimer=speech_proxy_disclaimer,
        coach_include=bool((prof.speech_analysis or {}).get("coach_include_speech_section", True)),
    )
    report = generate_coach_report(
        router=executor.router,
        provider=executor.provider,
        session=session,
        feedback=fb,
    )
    report = _merge_speech_coach_report(report, speech_session_report, speech_proxy_disclaimer)
    session.coach_report = report.model_dump()
    manager.save(session)
    return report


def _merge_speech_feedback(
    fb: FeedbackPacket,
    *,
    speech_session_report: dict[str, Any] | None,
    speech_proxy_disclaimer: str | None,
    coach_include: bool,
) -> FeedbackPacket:
    if not speech_session_report or not coach_include:
        return fb
    ss_strengths = list(speech_session_report.get("strengths") or [])[:8]
    ss_risks = list(speech_session_report.get("risks") or [])[:8]
    return fb.model_copy(
        update={
            "speech_session_report": speech_session_report,
            "speech_proxy_disclaimer": speech_proxy_disclaimer,
            "strengths": list(dict.fromkeys(list(fb.strengths) + ss_strengths)),
            "risks": list(dict.fromkeys(list(fb.risks) + ss_risks)),
        }
    )


def _merge_speech_coach_report(
    report: CoachReport,
    speech_session_report: dict[str, Any] | None,
    speech_proxy_disclaimer: str | None,
) -> CoachReport:
    if not speech_session_report:
        return report
    lim = []
    if speech_proxy_disclaimer:
        lim.append(speech_proxy_disclaimer)
    return report.model_copy(
        update={
            "speech_report": speech_session_report,
            "speech_strengths": list(speech_session_report.get("strengths") or [])[:12],
            "speech_risks": list(speech_session_report.get("risks") or [])[:12],
            "proxy_limitations": lim,
        }
    )
