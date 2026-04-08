"""Quality control nodes for discussion graph."""

from __future__ import annotations

from app.agent_runtime_v2.policy.quality_policy import QualityPolicy
from app.agent_runtime_v2.verifier.base import QualityVerifier
from app.agent_runtime_v2.state.graph_state import DiscussionGraphState
from app.runtime.schemas.agent import AgentReply
from app.runtime.schemas.session import SessionContext


def quality_check(
    state: DiscussionGraphState,
    session: SessionContext,
    reply: AgentReply | None,
    *,
    policy: QualityPolicy,
    verifier: QualityVerifier,
) -> str:
    """Policy + verifier driven quality gate.

    Returns one of: pass | repair | interrupt
    """
    if reply is None:
        state.quality_flags = []
        state.quality_decision = "pass"
        state.moderation_action = "accept"
        return "pass"

    d = verifier.verify(session=session, reply=reply, policy=policy)
    state.quality_flags = list(d.flags or [])
    if d.decision == "pass":
        state.quality_decision = "pass"
        state.moderation_action = "accept"
        return "pass"
    if d.decision == "repair" and state.repair_count < int(policy.max_repairs):
        state.quality_decision = "repair"
        state.moderation_action = "repair"
        state.max_repairs = int(policy.max_repairs)
        return "repair"
    if bool(policy.enable_interrupt) and bool(policy.interrupt_after_max_repairs):
        state.quality_decision = "interrupt"
        state.moderation_action = "interrupt_for_review"
        state.interrupt_reason = "quality_failed_after_max_repairs"
        return "interrupt"
    state.quality_decision = "pass"
    state.moderation_action = "accept_despite_quality_flags"
    return "pass"


def repair_turn(
    state: DiscussionGraphState,
    session: SessionContext,
    reply: AgentReply | None,
) -> tuple[SessionContext, AgentReply | None]:
    """Minimal deterministic repair pass.

    Phase-4 intentionally avoids extra LLM calls and applies lightweight rewrite.
    """
    state.repair_count += 1
    if not session.turns:
        return session, reply
    last_turn = session.turns[-1]
    if last_turn.speaker_role == "user":
        return session, reply
    repaired = f"{last_turn.text.strip()} [REPAIR] Clarified with explicit topic linkage and a direct response."
    last_turn.text = repaired
    last_turn.metadata = {**(last_turn.metadata or {}), "quality_repaired": True, "repair_count": state.repair_count}
    if reply is not None:
        reply.text = repaired
        reply.metadata = {**(reply.metadata or {}), "quality_repaired": True, "repair_count": state.repair_count}
    return session, reply


def interrupt_for_review(state: DiscussionGraphState) -> None:
    state.interrupt_reason = state.interrupt_reason or "quality_interrupt"
    state.stop_reason = "interrupt_for_review"
