"""Analyzer + coach feedback."""

from __future__ import annotations

from pathlib import Path

from app.application.exceptions import SessionNotFoundError
from app.runtime.evaluation.analyzers import analyze_transcript_turns
from app.runtime.evaluation.feedback_packet import build_feedback_packet
from app.runtime.execution.feedback_runner import run_generate_feedback
from app.runtime.execution.turn_executor import TurnExecutor
from app.runtime.retrieval.router import build_repositories
from app.runtime.schemas.coach_report import CoachReport
from app.runtime.snapshot_loader import load_snapshot

from .session_service import SessionService


class FeedbackService:
    def __init__(self, session_service: SessionService) -> None:
        self._sessions = session_service

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

    def generate_feedback(self, session_id: str) -> CoachReport:
        ctx = self._sessions.manager.load(session_id)
        if not ctx or not ctx.snapshot_dir:
            raise SessionNotFoundError(session_id)
        ex = TurnExecutor.from_paths(Path(ctx.snapshot_dir), ctx)
        return run_generate_feedback(ex, self._sessions.manager)
