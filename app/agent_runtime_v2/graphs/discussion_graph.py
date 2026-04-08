"""Compiled LangGraph discussion flow for runtime V2.

This graph is shared by both single-step and multi-step discussion runs.
"""

from __future__ import annotations

from typing import Any, TypedDict

from app.agent_runtime_v2.nodes.generation_nodes import generate_turn, select_next_actor
from app.agent_runtime_v2.nodes.persistence_nodes import persist_session, stop_check
from app.agent_runtime_v2.nodes.quality_nodes import interrupt_for_review, quality_check, repair_turn
from app.agent_runtime_v2.policy.quality_policy import QualityPolicyResolver
from app.agent_runtime_v2.nodes.session_nodes import load_session
from app.agent_runtime_v2.store.event_logger import RuntimeEventLogger
from app.agent_runtime_v2.state.graph_state import DiscussionGraphState
from app.agent_runtime_v2.tools.session_tool import SessionTool
from app.agent_runtime_v2.verifier.heuristic import HeuristicQualityVerifier
from app.runtime.schemas.agent import AgentReply
from app.runtime.schemas.session import SessionContext


class DiscussionGraphData(TypedDict, total=False):
    run_id: str
    session_id: str
    runtime_profile_id: str
    phase: str
    last_role: str | None
    next_actor: str | None
    loop_index: int
    max_steps: int
    stop_reason: str | None
    run_status: str
    last_successful_node: str | None
    runtime_checkpoint_id: str | None
    trace_id: str | None
    emitted_turn_ids: list[str]
    quality_flags: list[str]
    repair_count: int
    max_repairs: int
    quality_decision: str | None
    moderation_action: str | None
    interrupt_reason: str | None
    review_id: str | None
    policy_id: str | None
    metadata: dict[str, Any]
    artifacts: dict[str, Any]
    events: list[dict]
    session: SessionContext | None
    reply: AgentReply | None
    replies: list[AgentReply]


def has_langgraph_support() -> bool:
    try:
        from langgraph.graph import StateGraph  # type: ignore # noqa: F401

        return True
    except Exception:
        return False


class DiscussionGraph:
    """Compiled graph for minimal discussion turns."""

    def __init__(self, session_tool: SessionTool, event_logger: RuntimeEventLogger) -> None:
        self._session_tool = session_tool
        self._event_logger = event_logger
        self._policy_resolver = QualityPolicyResolver()
        self._verifier = HeuristicQualityVerifier()
        self._compiled = None

    def _to_model(self, data: DiscussionGraphData) -> DiscussionGraphState:
        return DiscussionGraphState.model_validate(
            {
                "run_id": data.get("run_id"),
                "session_id": data.get("session_id"),
                "runtime_profile_id": data.get("runtime_profile_id", "default"),
                "phase": data.get("phase", "discussion"),
                "last_role": data.get("last_role"),
                "next_actor": data.get("next_actor"),
                "loop_index": data.get("loop_index", 0),
                "max_steps": data.get("max_steps", 1),
                "stop_reason": data.get("stop_reason"),
                "run_status": data.get("run_status", "running"),
                "last_successful_node": data.get("last_successful_node"),
                "runtime_checkpoint_id": data.get("runtime_checkpoint_id"),
                "trace_id": data.get("trace_id"),
                "emitted_turn_ids": list(data.get("emitted_turn_ids") or []),
                "quality_flags": list(data.get("quality_flags") or []),
                "repair_count": int(data.get("repair_count", 0)),
                "max_repairs": int(data.get("max_repairs", 1)),
                "quality_decision": data.get("quality_decision"),
                "moderation_action": data.get("moderation_action"),
                "interrupt_reason": data.get("interrupt_reason"),
                "review_id": data.get("review_id"),
                "policy_id": data.get("policy_id"),
                "metadata": dict(data.get("metadata") or {}),
                "artifacts": dict(data.get("artifacts") or {}),
                "events": list(data.get("events") or []),
            }
        )

    def _append_event(
        self,
        data: DiscussionGraphData,
        *,
        node_name: str,
        success: bool,
        error_summary: str | None = None,
    ) -> list[dict]:
        evt = self._event_logger.log(
            run_id=str(data.get("run_id") or ""),
            session_id=str(data.get("session_id") or ""),
            backend="v2",
            node_name=node_name,
            next_actor=data.get("next_actor"),
            stop_reason=data.get("stop_reason"),
            success=success,
            error_summary=error_summary,
            trace_id=data.get("trace_id"),
            checkpoint_id=data.get("runtime_checkpoint_id"),
            quality_decision=data.get("quality_decision"),
            interrupt_reason=data.get("interrupt_reason"),
            repair_count=data.get("repair_count"),
            quality_flags=list(data.get("quality_flags") or []),
            review_id=data.get("review_id"),
            policy_id=data.get("policy_id"),
        )
        events = list(data.get("events") or [])
        events.append(evt)
        return events

    @staticmethod
    def _merge_emitted(existing: list[str] | None, incoming: list[str] | None) -> list[str]:
        out = list(existing or [])
        seen = set(out)
        for tid in incoming or []:
            if tid in seen:
                continue
            seen.add(tid)
            out.append(tid)
        return out

    def _node_load_session(self, data: DiscussionGraphData) -> DiscussionGraphData:
        state = self._to_model(data)
        session = load_session(state, self._session_tool)
        return {
            "session": session,
            "phase": state.phase,
            "last_role": state.last_role,
            "run_status": "running",
            "last_successful_node": "load_session",
            "events": self._append_event(data, node_name="load_session", success=True),
        }

    def _node_select_next_actor(self, data: DiscussionGraphData) -> DiscussionGraphData:
        state = self._to_model(data)
        session = data.get("session")
        if session is None:
            state.stop_reason = "error"
            return {
                "stop_reason": state.stop_reason,
                "run_status": "failed",
                "events": self._append_event(
                    {**data, "stop_reason": state.stop_reason},
                    node_name="select_next_actor",
                    success=False,
                    error_summary="Session object missing in graph state.",
                ),
            }
        next_role = select_next_actor(state, session)
        return {
            "next_actor": next_role,
            "stop_reason": state.stop_reason,
            "last_successful_node": "select_next_actor",
            "events": self._append_event(
                {**data, "next_actor": next_role, "stop_reason": state.stop_reason},
                node_name="select_next_actor",
                success=True,
            ),
        }

    def _node_generate_turn(self, data: DiscussionGraphData) -> DiscussionGraphData:
        state = self._to_model(data)
        session = data.get("session")
        if session is None:
            state.stop_reason = "error"
            return {
                "stop_reason": state.stop_reason,
                "run_status": "failed",
                "events": self._append_event(
                    {**data, "stop_reason": state.stop_reason},
                    node_name="generate_turn",
                    success=False,
                    error_summary="Session object missing in graph state.",
                ),
            }
        before_turn_ids = [t.turn_id for t in session.turns]
        out_session, reply = generate_turn(state, session)
        after_turn_ids = [t.turn_id for t in out_session.turns]
        pending = [tid for tid in after_turn_ids if tid not in set(before_turn_ids)]
        replies = list(data.get("replies") or [])
        if reply is not None:
            replies.append(reply)
        artifacts = dict(data.get("artifacts") or {})
        artifacts["pending_turn_ids"] = pending
        artifacts["draft_reply_text"] = reply.text if reply else None
        return {
            "session": out_session,
            "reply": reply,
            "replies": replies,
            "last_role": state.last_role,
            "stop_reason": state.stop_reason,
            "artifacts": artifacts,
            "last_successful_node": "generate_turn",
            "events": self._append_event(
                {**data, "stop_reason": state.stop_reason},
                node_name="generate_turn",
                success=True,
            ),
        }

    def _node_quality_check(self, data: DiscussionGraphData) -> DiscussionGraphData:
        state = self._to_model(data)
        session = data.get("session")
        reply = data.get("reply")
        if session is None:
            state.stop_reason = "error"
            state.quality_decision = "interrupt"
            return {
                "stop_reason": "error",
                "quality_decision": state.quality_decision,
                "run_status": "failed",
                "events": self._append_event(
                    {**data, "stop_reason": "error", "quality_decision": "interrupt"},
                    node_name="quality_check",
                    success=False,
                    error_summary="Session object missing in quality_check.",
                ),
            }
        policy = self._policy_resolver.resolve(state.runtime_profile_id, role=state.next_actor)
        decision = quality_check(
            state,
            session,
            reply,
            policy=policy,
            verifier=self._verifier,
        )
        return {
            "quality_flags": list(state.quality_flags or []),
            "quality_decision": decision,
            "moderation_action": state.moderation_action,
            "interrupt_reason": state.interrupt_reason,
            "max_repairs": int(policy.max_repairs),
            "policy_id": policy.policy_id,
            "metadata": {**dict(data.get("metadata") or {}), "quality_policy_snapshot": policy.model_dump(mode="json")},
            "last_successful_node": "quality_check",
            "events": self._append_event(
                {
                    **data,
                    "quality_decision": decision,
                    "quality_flags": list(state.quality_flags or []),
                    "interrupt_reason": state.interrupt_reason,
                    "repair_count": state.repair_count,
                    "policy_id": policy.policy_id,
                },
                node_name="quality_check",
                success=True,
            ),
        }

    def _node_repair_turn(self, data: DiscussionGraphData) -> DiscussionGraphData:
        state = self._to_model(data)
        session = data.get("session")
        reply = data.get("reply")
        if session is None:
            state.stop_reason = "error"
            return {
                "stop_reason": "error",
                "run_status": "failed",
                "events": self._append_event(
                    {**data, "stop_reason": "error"},
                    node_name="repair_turn",
                    success=False,
                    error_summary="Session object missing in repair_turn.",
                ),
            }
        out_session, out_reply = repair_turn(state, session, reply)
        replies = list(data.get("replies") or [])
        if replies and out_reply is not None:
            replies[-1] = out_reply
        artifacts = dict(data.get("artifacts") or {})
        artifacts["draft_reply_text"] = out_reply.text if out_reply else artifacts.get("draft_reply_text")
        return {
            "session": out_session,
            "reply": out_reply,
            "replies": replies,
            "repair_count": state.repair_count,
            "artifacts": artifacts,
            "last_successful_node": "repair_turn",
            "events": self._append_event(
                {**data, "repair_count": state.repair_count},
                node_name="repair_turn",
                success=True,
            ),
        }

    def _node_interrupt_for_review(self, data: DiscussionGraphData) -> DiscussionGraphData:
        state = self._to_model(data)
        interrupt_for_review(state)
        return {
            "interrupt_reason": state.interrupt_reason,
            "stop_reason": state.stop_reason,
            "quality_decision": "interrupt",
            "moderation_action": "interrupt_for_review",
            "last_successful_node": "interrupt_for_review",
            "events": self._append_event(
                {
                    **data,
                    "stop_reason": state.stop_reason,
                    "interrupt_reason": state.interrupt_reason,
                    "quality_decision": "interrupt",
                },
                node_name="interrupt_for_review",
                success=True,
            ),
        }

    def _node_persist_session(self, data: DiscussionGraphData) -> DiscussionGraphData:
        state = self._to_model(data)
        session = data.get("session")
        artifacts = dict(data.get("artifacts") or {})
        pending = list(artifacts.get("pending_turn_ids") or [])
        if session is not None:
            persist_session(state, session, self._session_tool)
        artifacts["pending_turn_ids"] = []
        return {
            "loop_index": state.loop_index,
            "emitted_turn_ids": self._merge_emitted(data.get("emitted_turn_ids"), pending),
            "artifacts": artifacts,
            "last_successful_node": "persist_session",
            "events": self._append_event(
                {**data, "loop_index": state.loop_index},
                node_name="persist_session",
                success=True,
            ),
        }

    def _node_stop_check(self, data: DiscussionGraphData) -> DiscussionGraphData:
        state = self._to_model(data)
        done = stop_check(state)
        if done:
            if state.stop_reason in {"need_user_input", "max_steps_reached", "interrupt_for_review"}:
                state.run_status = "interrupted"
            elif state.stop_reason in {"phase_complete", "completed"}:
                state.run_status = "completed"
            elif state.stop_reason in {"error"}:
                state.run_status = "failed"
            else:
                state.stop_reason = state.stop_reason or "completed"
                state.run_status = "completed"
        return {
            "stop_reason": state.stop_reason,
            "run_status": state.run_status,
            "last_successful_node": "stop_check",
            "events": self._append_event(
                {
                    **data,
                    "stop_reason": state.stop_reason,
                    "quality_decision": state.quality_decision,
                    "interrupt_reason": state.interrupt_reason,
                },
                node_name="stop_check",
                success=True,
            ),
        }

    @staticmethod
    def _route_after_select_next_actor(data: DiscussionGraphData) -> str:
        if data.get("stop_reason"):
            return "stop_check"
        if data.get("next_actor") == "user":
            return "stop_check"
        return "generate_turn"

    @staticmethod
    def _route_after_quality_check(data: DiscussionGraphData) -> str:
        d = str(data.get("quality_decision") or "pass")
        if d == "repair":
            return "repair_turn"
        if d == "interrupt":
            return "interrupt_for_review"
        return "persist_session"

    @staticmethod
    def _route_after_stop_check(data: DiscussionGraphData) -> str:
        if data.get("stop_reason") is not None:
            return "end"
        return "select_next_actor"

    def build_compiled_graph(self):
        if self._compiled is not None:
            return self._compiled
        if not has_langgraph_support():
            raise RuntimeError(
                "LangGraph is not available. Install optional dependency `langgraph` "
                "or use AGENT_RUNTIME_BACKEND=v1."
            )
        from langgraph.graph import END, START, StateGraph  # type: ignore

        g = StateGraph(DiscussionGraphData)
        g.add_node("load_session", self._node_load_session)
        g.add_node("select_next_actor", self._node_select_next_actor)
        g.add_node("generate_turn", self._node_generate_turn)
        g.add_node("quality_check", self._node_quality_check)
        g.add_node("repair_turn", self._node_repair_turn)
        g.add_node("interrupt_for_review", self._node_interrupt_for_review)
        g.add_node("persist_session", self._node_persist_session)
        g.add_node("stop_check", self._node_stop_check)

        g.add_edge(START, "load_session")
        g.add_edge("load_session", "select_next_actor")
        g.add_conditional_edges(
            "select_next_actor",
            self._route_after_select_next_actor,
            {"generate_turn": "generate_turn", "stop_check": "stop_check"},
        )
        g.add_edge("generate_turn", "quality_check")
        g.add_conditional_edges(
            "quality_check",
            self._route_after_quality_check,
            {
                "persist_session": "persist_session",
                "repair_turn": "repair_turn",
                "interrupt_for_review": "interrupt_for_review",
            },
        )
        g.add_edge("repair_turn", "quality_check")
        g.add_edge("interrupt_for_review", "stop_check")
        g.add_edge("persist_session", "stop_check")
        g.add_conditional_edges(
            "stop_check",
            self._route_after_stop_check,
            {"select_next_actor": "select_next_actor", "end": END},
        )
        self._compiled = g.compile()
        return self._compiled

    def run(
        self,
        state: DiscussionGraphState,
        *,
        max_steps: int | None = None,
    ) -> tuple[DiscussionGraphState, SessionContext, AgentReply | None, list[AgentReply]]:
        graph = self.build_compiled_graph()
        effective_steps = int(max_steps if max_steps is not None else state.max_steps)
        state.max_steps = max(1, effective_steps)
        state.run_status = "running"
        state.stop_reason = None if state.stop_reason in {"completed", "max_steps_reached"} else state.stop_reason
        initial: DiscussionGraphData = {
            **state.model_dump(),
            "session": None,
            "reply": None,
            "replies": [],
        }
        result: DiscussionGraphData = graph.invoke(initial, config={"recursion_limit": max(64, state.max_steps * 8)})
        final_state = self._to_model(result)
        session = result.get("session") or self._session_tool.load(final_state.session_id)
        if session is None:
            raise RuntimeError(f"Session not found after graph run: {final_state.session_id}")
        reply = result.get("reply")
        replies = list(result.get("replies") or [])
        return final_state, session, reply, replies
