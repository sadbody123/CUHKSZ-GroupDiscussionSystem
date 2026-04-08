"""Generation nodes.

Phase 1 bridges to V1 TurnExecutor to avoid breaking the current runtime.
"""

from __future__ import annotations

from pathlib import Path

from app.agent_runtime_v2.state.graph_state import DiscussionGraphState
from app.runtime.execution.turn_executor import TurnExecutor
from app.runtime.schemas.agent import AgentReply
from app.runtime.schemas.session import SessionContext


def select_next_actor(state: DiscussionGraphState, session: SessionContext) -> str:
    if not session.snapshot_dir:
        state.stop_reason = "error"
        return "stop"
    ex = TurnExecutor.from_paths(Path(session.snapshot_dir), session)
    next_role = ex.sm.peek_next_role(session, state.last_role)
    state.next_actor = next_role
    if next_role == "user":
        state.stop_reason = "need_user_input"
    return next_role


def generate_turn(
    state: DiscussionGraphState,
    session: SessionContext,
) -> tuple[SessionContext, AgentReply | None]:
    if not session.snapshot_dir:
        state.stop_reason = "error"
        return session, None
    ex = TurnExecutor.from_paths(Path(session.snapshot_dir), session)
    out_session, reply = ex.run_next_turn()
    state.last_role = out_session.turns[-1].speaker_role if out_session.turns else None
    if reply is None:
        state.stop_reason = "need_user_input"
    return out_session, reply
