"""Auto-advance discussion with optional user filler lines."""

from __future__ import annotations

from app.runtime.enums import RoleType
from app.runtime.execution.turn_executor import TurnExecutor
from app.runtime.schemas.agent import AgentReply
from app.runtime.schemas.session import SessionContext


def auto_run_discussion(
    executor: TurnExecutor,
    *,
    max_steps: int = 4,
    auto_fill_user: bool = True,
) -> tuple[SessionContext, list[AgentReply]]:
    """Run up to ``max_steps`` agent generations. If next role is user, optionally inject a stub user line."""
    out: list[AgentReply] = []
    session = executor.session
    for _ in range(max_steps):
        last = session.turns[-1].speaker_role if session.turns else None
        nr = executor.sm.peek_next_role(session, last)
        if nr == RoleType.USER.value:
            if not auto_fill_user:
                break
            session = executor.submit_user_turn("[auto] Continuing the discussion with a brief follow-up.")
        rep = executor.run_next_turn()[1]
        if rep is None:
            continue
        out.append(rep)
    return session, out
