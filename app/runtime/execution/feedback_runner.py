"""Coach feedback generation from transcript."""

from __future__ import annotations

from app.runtime.agents.coach_agent import generate_coach_report
from app.runtime.evaluation.analyzers import analyze_transcript_turns
from app.runtime.profile_resolver import resolve_runtime_profile
from app.runtime.evaluation.feedback_packet import build_feedback_packet
from app.runtime.execution.turn_executor import TurnExecutor
from app.runtime.retrieval.router import build_repositories
from app.runtime.schemas.coach_report import CoachReport
from app.runtime.session.manager import SessionManager


def run_generate_feedback(executor: TurnExecutor, manager: SessionManager) -> CoachReport:
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
    report = generate_coach_report(
        router=executor.router,
        provider=executor.provider,
        session=session,
        feedback=fb,
    )
    session.coach_report = report.model_dump()
    manager.save(session)
    return report
