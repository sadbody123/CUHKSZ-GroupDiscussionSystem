"""Session lifecycle nodes."""

from __future__ import annotations

from app.agent_runtime_v2.state.graph_state import DiscussionGraphState
from app.agent_runtime_v2.tools.session_tool import SessionTool
from app.runtime.schemas.session import SessionContext


def load_session(state: DiscussionGraphState, session_tool: SessionTool) -> SessionContext:
    ctx = session_tool.load(state.session_id)
    if ctx is None:
        raise ValueError(f"Session not found: {state.session_id}")
    state.phase = ctx.phase
    state.last_role = ctx.turns[-1].speaker_role if ctx.turns else None
    if ctx.phase == "feedback":
        state.stop_reason = "phase_complete"
    return ctx
