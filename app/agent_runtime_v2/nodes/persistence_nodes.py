"""Persistence and stop-check nodes."""

from __future__ import annotations

from app.agent_runtime_v2.facade.cancel_signal import is_cancel_requested
from app.agent_runtime_v2.state.graph_state import DiscussionGraphState
from app.agent_runtime_v2.tools.session_tool import SessionTool
from app.runtime.schemas.session import SessionContext


def persist_session(state: DiscussionGraphState, session: SessionContext, session_tool: SessionTool) -> None:
    session_tool.save(session)
    state.loop_index += 1


def stop_check(state: DiscussionGraphState) -> bool:
    if is_cancel_requested(state.session_id):
        state.stop_reason = "cancelled"
        return True
    if state.stop_reason:
        return True
    if state.loop_index >= state.max_steps:
        state.stop_reason = "max_steps_reached"
        return True
    return False
