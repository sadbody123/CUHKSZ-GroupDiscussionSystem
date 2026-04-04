"""Explicit session phase machine (no LLM)."""

from __future__ import annotations

from app.runtime.enums import RoleType, SessionPhase
from app.runtime.orchestrator import policies as pol
from app.runtime.schemas.context_packet import RoleContextPacket, TurnPlan
from app.runtime.schemas.session import SessionContext
from app.runtime.schemas.transcript import TranscriptTurn
from app.runtime.retrieval.router import RoleRouter


class SessionStateMachine:
    """Advance phases and suggest next speaker roles."""

    def __init__(self, router: RoleRouter, orchestration: dict | None = None) -> None:
        self.router = router
        self._orch = orchestration or {}

    def advance_phase(self, ctx: SessionContext) -> str:
        """Update ``ctx.phase`` using transcript length and return the new phase."""
        t = len(ctx.turns)
        ph = ctx.phase
        intro_min = int(self._orch.get("intro_turn_threshold", pol.INTRO_MIN_TURNS))
        disc_max = int(self._orch.get("discussion_turn_threshold", pol.DISCUSSION_MAX_TURNS))
        sum_min = int(self._orch.get("summary_min_turns", pol.SUMMARY_MIN_TURNS))

        if ph == SessionPhase.PREPARE.value and ctx.topic_id:
            ctx.phase = SessionPhase.INTRO.value
            return ctx.phase
        if ph == SessionPhase.INTRO.value and t >= intro_min:
            ctx.phase = SessionPhase.DISCUSSION.value
            return ctx.phase
        if ph == SessionPhase.DISCUSSION.value and t >= disc_max:
            ctx.phase = SessionPhase.SUMMARY.value
            return ctx.phase
        if ph == SessionPhase.SUMMARY.value and t >= disc_max + sum_min:
            ctx.phase = SessionPhase.FEEDBACK.value
            return ctx.phase
        if ph == SessionPhase.FEEDBACK.value:
            ctx.phase = SessionPhase.ENDED.value
            return ctx.phase
        return ctx.phase

    def peek_next_role(self, session: SessionContext, last_role: str | None) -> str:
        """Suggest next speaker without mutating ``session``."""
        ctx = session.model_copy(deep=True)
        return self.suggest_next_role(ctx, last_role)

    def suggest_next_role(self, ctx: SessionContext, last_role: str | None) -> str:
        phase = ctx.phase
        lr = (last_role or "").lower()
        if phase == SessionPhase.PREPARE.value:
            return RoleType.USER.value
        if phase == SessionPhase.INTRO.value:
            return RoleType.USER.value if lr != RoleType.USER.value else RoleType.MODERATOR.value
        if phase == SessionPhase.DISCUSSION.value:
            if lr == RoleType.USER.value:
                return RoleType.OPPONENT.value if hash(ctx.session_id) % 2 == 0 else RoleType.ALLY.value
            if lr in (RoleType.ALLY.value, RoleType.OPPONENT.value):
                return RoleType.USER.value
            if lr == RoleType.MODERATOR.value:
                return RoleType.USER.value
            return RoleType.USER.value
        if phase == SessionPhase.SUMMARY.value:
            return RoleType.MODERATOR.value if lr != RoleType.MODERATOR.value else RoleType.USER.value
        if phase == SessionPhase.FEEDBACK.value:
            return RoleType.COACH.value
        return RoleType.USER.value

    def build_turn_plan(
        self,
        *,
        session_id: str,
        topic_id: str | None,
        phase: str,
        last_role: str | None,
        transcript_turns: list[TranscriptTurn],
    ) -> TurnPlan:
        ctx = SessionContext(
            session_id=session_id,
            topic_id=topic_id,
            phase=phase,
            turns=list(transcript_turns),
        )
        new_phase = self.advance_phase(ctx)
        next_role = self.suggest_next_role(ctx, last_role)
        pkt: RoleContextPacket = self.router.build_context_packet(
            role=next_role,
            topic_id=topic_id,
            session_phase=new_phase,
            top_k=5,
        )
        reason = f"phase={new_phase} last_role={last_role} turns={len(transcript_turns)}"
        return TurnPlan(
            session_id=session_id,
            phase=new_phase,
            next_role=next_role,
            reason=reason,
            context_packet=pkt.model_dump(),
            metadata={"previous_phase": phase, "updated_phase": new_phase},
        )
