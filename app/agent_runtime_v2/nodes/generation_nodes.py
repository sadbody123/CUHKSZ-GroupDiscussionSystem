"""Generation nodes.

Phase 1 bridges to V1 TurnExecutor to avoid breaking the current runtime.
"""

from __future__ import annotations

from pathlib import Path

from app.agent_runtime_v2.state.graph_state import DiscussionGraphState
from app.runtime.execution.reply_postprocessor import postprocess_reply
from app.runtime.execution.turn_executor import TurnExecutor
from app.runtime.schemas.agent import AgentReply
from app.runtime.schemas.session import SessionContext


def select_next_actor(state: DiscussionGraphState, session: SessionContext) -> str:
    if not session.snapshot_dir:
        state.stop_reason = "error"
        return "stop"

    # Check for pending activation queue (consecutive agent turns)
    pending = list(session.activation_queue)
    if pending:
        next_agent = pending.pop(0)
        session.activation_queue = pending
        state.next_actor = next_agent
        state.pending_actors = pending
        if not pending and not getattr(session, "allow_consecutive_agent_turns", False):
            state.stop_reason = "need_user_input"
        return next_agent

    # Run activation engine when there are participants
    if session.participants:
        from app.runtime.orchestrator.activation import ActivationEngine

        engine = ActivationEngine()
        strategy = getattr(session, "activation_strategy", "list") or "list"
        # Gather last user text for natural activation
        user_text = ""
        for t in reversed(session.turns):
            if t.speaker_role == "user":
                user_text = t.text or ""
                break

        plan = engine.activate(session, strategy, user_text=user_text, last_role=state.last_role)
        if plan.participant_ids:
            # First agent speaks now; rest go to activation queue
            state.next_actor = plan.participant_ids[0]
            state.pending_actors = plan.participant_ids
            session.activation_queue = plan.participant_ids[1:]
            if len(plan.participant_ids) <= 1:
                state.stop_reason = "need_user_input"
            return plan.participant_ids[0]

        state.next_actor = "user"
        state.stop_reason = "need_user_input"
        return "user"

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
    if reply is not None:
        reply.text = postprocess_reply(reply.text)
    if reply is None:
        state.stop_reason = "need_user_input"
    return out_session, reply
