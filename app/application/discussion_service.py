"""Discussion turns: submit user, run next, auto-run, status."""

from __future__ import annotations

from pathlib import Path

from app.application.config import AppConfig
from app.application.exceptions import PhaseConflictError, SessionNotFoundError
from app.runtime.enums import RoleType
from app.runtime.execution.discussion_loop import auto_run_discussion
from app.runtime.execution.turn_executor import TurnExecutor
from app.runtime.orchestrator.state_machine import SessionStateMachine
from app.runtime.retrieval.router import RoleRouter, build_repositories
from app.runtime.schemas.agent import AgentReply
from app.runtime.schemas.session import SessionContext
from app.runtime.snapshot_loader import load_snapshot

from .session_service import SessionService


class DiscussionService:
    def __init__(self, config: AppConfig, session_service: SessionService) -> None:
        self._config = config
        self._sessions = session_service

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
        return ex.session

    def run_next_turn(self, session_id: str) -> tuple[SessionContext, AgentReply | None, str]:
        ctx = self._sessions.manager.load(session_id)
        if not ctx:
            raise SessionNotFoundError(session_id)
        if ctx.phase == "feedback":
            raise PhaseConflictError("Discussion already in feedback phase")
        ex = self._executor(ctx)
        sess, reply = ex.run_next_turn()
        self._sessions.manager.save(sess)
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
        return sess, replies

    def get_session_status(self, session_id: str) -> dict:
        ctx = self._sessions.get_session(session_id)
        last = ctx.turns[-1].speaker_role if ctx.turns else None
        sm = None
        if ctx.snapshot_dir:
            try:
                bundle = load_snapshot(Path(ctx.snapshot_dir))
                ped, top, ev, doc, _src = build_repositories(bundle)
                sm = SessionStateMachine(RoleRouter(ped, top, ev, doc))
            except OSError:
                sm = None
        can_run = ctx.phase != "feedback" and bool(ctx.snapshot_dir)
        next_hint = None
        if sm and can_run:
            next_hint = sm.peek_next_role(ctx, last)
        feedback_ready = len(ctx.turns) > 0
        coach_preview = None
        if ctx.coach_report and isinstance(ctx.coach_report, dict):
            txt = str(ctx.coach_report.get("text") or "")
            coach_preview = txt[:1200] if txt else None
        return {
            "session_id": ctx.session_id,
            "topic_id": ctx.topic_id,
            "phase": ctx.phase,
            "runtime_profile_id": ctx.runtime_profile_id,
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
        }
