"""Application-facing runtime V2 facade."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from app.agent_runtime_v2.graphs.discussion_graph import DiscussionGraph
from app.agent_runtime_v2.graphs.discussion_graph import has_langgraph_support
from app.agent_runtime_v2.review.service import RuntimeReviewService
from app.agent_runtime_v2.review.store import ReviewQueueStore
from app.agent_runtime_v2.store.checkpoint_store import FileCheckpointStore
from app.agent_runtime_v2.store.event_logger import RuntimeEventLogger
from app.agent_runtime_v2.state.graph_state import DiscussionGraphState
from app.agent_runtime_v2.tools.session_tool import SessionTool
from app.application.config import AppConfig
from app.application.exceptions import PhaseConflictError, SessionNotFoundError
from app.application.feedback_service import FeedbackService
from app.application.session_service import SessionService
from app.runtime.schemas.agent import AgentReply
from app.runtime.schemas.session import SessionContext
from app.runtime.schemas.transcript import TranscriptTurn


class AgentRuntimeFacade:
    """V2 runtime facade for discussion workflows.

    Phase-1 intentionally reuses V1 retrieval/session data structures.
    """

    def __init__(self, config: AppConfig, session_service: SessionService) -> None:
        self._config = config
        self._sessions = session_service
        self._session_tool = SessionTool(session_service)
        self._checkpoint_store = FileCheckpointStore(config.agent_runtime_v2_dir / "checkpoints")
        self._event_logger = RuntimeEventLogger(config.agent_runtime_v2_dir / "events" / "runtime_v2_events.jsonl")
        self._review_service = RuntimeReviewService(
            ReviewQueueStore(config.agent_runtime_v2_dir / "review_queue")
        )
        self._graph = DiscussionGraph(self._session_tool, self._event_logger)

    def _classify_status(self, stop_reason: str | None) -> str:
        if stop_reason in {"need_user_input", "max_steps_reached", "interrupt_for_review", "cancelled"}:
            return "interrupted"
        if stop_reason in {"error"}:
            return "failed"
        return "completed"

    @staticmethod
    def _utc_now_iso() -> str:
        return datetime.now(timezone.utc).isoformat()

    def _validate_resume_checkpoint(self, ctx: SessionContext, payload: dict) -> None:
        state = payload.get("state") or {}
        emitted = list(state.get("emitted_turn_ids") or [])
        session_turn_ids = {t.turn_id for t in ctx.turns}
        missing = [tid for tid in emitted if tid not in session_turn_ids]
        if missing:
            raise SessionNotFoundError(
                f"Checkpoint/session mismatch: missing emitted turns in session: {missing[:3]}"
            )

    def run(
        self,
        session_id: str,
        *,
        max_steps: int = 1,
        run_id: str | None = None,
        resume: bool = False,
    ) -> tuple[SessionContext, list[AgentReply], DiscussionGraphState]:
        ctx = self._sessions.manager.load(session_id)
        if not ctx:
            raise SessionNotFoundError(session_id)
        if ctx.phase == "feedback":
            raise PhaseConflictError("Discussion already in feedback phase")
        if not has_langgraph_support():
            raise RuntimeError("V2 backend requires `langgraph`. Use backend=v1 or install langgraph.")

        state: DiscussionGraphState
        if resume:
            payload = self._checkpoint_store.load(run_id) if run_id else self._checkpoint_store.load_latest_for_session(session_id)
            if payload is None:
                raise SessionNotFoundError(f"No V2 checkpoint found for session_id={session_id}")
            if str(payload.get("session_id")) != session_id:
                raise SessionNotFoundError("Checkpoint session_id mismatch")
            if str(payload.get("status")) == "completed":
                prev_state = DiscussionGraphState.model_validate(payload.get("state") or {})
                return ctx, [], prev_state
            self._validate_resume_checkpoint(ctx, payload)
            state = DiscussionGraphState.model_validate(payload.get("state") or {})
            state.stop_reason = None
            state.max_steps = max(state.loop_index + 1, state.loop_index + int(max_steps))
            state.run_status = "running"
        else:
            rid = run_id or str(uuid4())
            state = DiscussionGraphState.from_session(
                ctx,
                run_id=rid,
                max_steps=max_steps,
                trace_id=f"trace-{rid}",
            )
        state.max_steps = max(state.loop_index + 1, int(max_steps) if not resume else state.max_steps)
        start_ckpt = self._checkpoint_store.save(state, status="running")
        state.checkpoint_id = start_ckpt

        from app.agent_runtime_v2.facade.cancel_signal import is_cancel_requested

        if is_cancel_requested(state.session_id):
            state.run_status = "interrupted"
            state.stop_reason = "cancelled"
            self._checkpoint_store.save(state, status="interrupted")
            self._event_logger.log(
                run_id=state.run_id,
                session_id=state.session_id,
                backend="v2",
                node_name="run",
                next_actor=state.next_actor,
                stop_reason="cancelled",
                success=True,
                trace_id=state.trace_id,
                checkpoint_id=start_ckpt,
            )
            ctx = self._sessions.manager.load(session_id)
            if not ctx:
                raise SessionNotFoundError(session_id)
            self._event_logger.flush()
            return ctx, [], state

        try:
            final_state, sess, _reply, replies = self._graph.run(state, max_steps=state.max_steps)
            # Interrupt path keeps generated draft in-memory for review, but must not leak
            # draft turns into persisted session transcript before explicit approval/apply.
            if final_state.stop_reason == "interrupt_for_review":
                pending_turn_ids = list((final_state.artifacts or {}).get("pending_turn_ids") or [])
                if pending_turn_ids:
                    pending_set = set(pending_turn_ids)
                    sess.turns = [t for t in sess.turns if t.turn_id not in pending_set]
                    final_state.artifacts = {**dict(final_state.artifacts or {}), "pending_turn_ids": []}
            final_state.run_status = self._classify_status(final_state.stop_reason)
            if final_state.run_status == "completed":
                final_status = "completed"
            elif final_state.run_status == "failed":
                final_status = "failed"
            else:
                final_status = "interrupted"
            final_ckpt = self._checkpoint_store.save(final_state, status=final_status)
            final_state.checkpoint_id = final_ckpt
            if final_state.stop_reason == "interrupt_for_review":
                draft_reply_summary = None
                try:
                    draft_reply_summary = str((final_state.artifacts or {}).get("draft_reply_text") or "")[:500]
                except Exception:
                    draft_reply_summary = None
                review_item = self._review_service.create_item(
                    session_id=final_state.session_id,
                    run_id=final_state.run_id,
                    checkpoint_id=final_ckpt,
                    topic_id=ctx.topic_id,
                    reason="quality_interrupt",
                    interrupt_reason=final_state.interrupt_reason,
                    quality_flags=list(final_state.quality_flags or []),
                    draft_reply_text=str((final_state.artifacts or {}).get("draft_reply_text") or "") or None,
                    draft_reply_summary=draft_reply_summary,
                    metadata={
                        "policy_id": final_state.policy_id,
                        "quality_decision": final_state.quality_decision,
                        "next_actor": final_state.next_actor,
                    },
                )
                final_state.review_id = review_item.review_id
                final_ckpt = self._checkpoint_store.save(final_state, status=final_status)
                final_state.checkpoint_id = final_ckpt
                self._event_logger.log(
                    run_id=final_state.run_id,
                    session_id=final_state.session_id,
                    backend="v2",
                    node_name="review_item_created",
                    next_actor=final_state.next_actor,
                    stop_reason=final_state.stop_reason,
                    success=True,
                    trace_id=final_state.trace_id,
                    checkpoint_id=final_ckpt,
                    quality_decision=final_state.quality_decision,
                    interrupt_reason=final_state.interrupt_reason,
                    repair_count=final_state.repair_count,
                    quality_flags=list(final_state.quality_flags or []),
                    review_id=review_item.review_id,
                    policy_id=final_state.policy_id,
                )
            self._event_logger.log(
                run_id=final_state.run_id,
                session_id=final_state.session_id,
                backend="v2",
                node_name="run",
                next_actor=final_state.next_actor,
                stop_reason=final_state.stop_reason,
                success=True,
                trace_id=final_state.trace_id,
                checkpoint_id=final_ckpt,
                quality_decision=final_state.quality_decision,
                interrupt_reason=final_state.interrupt_reason,
                repair_count=final_state.repair_count,
                quality_flags=list(final_state.quality_flags or []),
                review_id=final_state.review_id,
                policy_id=final_state.policy_id,
            )
            self._event_logger.flush()
            return sess, replies, final_state
        except Exception as exc:
            state.run_status = "failed"
            state.stop_reason = "error"
            failed_ckpt = self._checkpoint_store.save(state, status="failed")
            self._event_logger.log(
                run_id=state.run_id,
                session_id=state.session_id,
                backend="v2",
                node_name="run",
                next_actor=state.next_actor,
                stop_reason="error",
                success=False,
                error_summary=str(exc)[:500],
                trace_id=state.trace_id,
                checkpoint_id=failed_ckpt,
            )
            self._event_logger.flush()
            raise

    def run_next_turn(self, session_id: str) -> tuple[SessionContext, AgentReply | None, str | None]:
        sess, replies, state = self.run(session_id, max_steps=1)
        reply = replies[-1] if replies else None
        return sess, reply, state.next_actor

    def auto_run_discussion(
        self,
        session_id: str,
        *,
        max_steps: int,
        auto_fill_user: bool = True,
    ) -> tuple[SessionContext, list[AgentReply]]:
        from app.agent_runtime_v2.facade.cancel_signal import get_cancel_event, clear_cancel

        cancel_evt = get_cancel_event(session_id)
        cancel_evt.clear()
        try:
            sess, replies, _state = self.run(session_id, max_steps=max_steps)
            return sess, replies
        finally:
            clear_cancel(session_id)

    def generate_feedback(self, session_id: str) -> dict:
        # V2 reuses V1's FeedbackService by design: the discussion loop and the
        # feedback/coach evaluation are separate concerns.  When V2 eventually
        # takes over the full discussion prompt path, feedback will remain a
        # separate graph detached from the turn-by-turn loop.
        report = FeedbackService(self._sessions).generate_feedback(session_id)
        return report.model_dump()

    def resume_run(self, session_id: str, run_id: str | None = None, *, additional_steps: int = 1) -> dict:
        payload = self._checkpoint_store.load(run_id) if run_id else self._checkpoint_store.load_latest_for_session(session_id)
        if payload is None:
            raise SessionNotFoundError(f"No V2 checkpoint found for session_id={session_id}")
        if str(payload.get("status")) == "completed":
            state = DiscussionGraphState.model_validate(payload.get("state") or {})
            ctx = self._sessions.manager.load(session_id)
            if not ctx:
                raise SessionNotFoundError(session_id)
            return {
                "run_id": state.run_id,
                "session_id": state.session_id,
                "checkpoint_id": payload.get("checkpoint_id"),
                "loop_index": state.loop_index,
                "next_actor": state.next_actor,
                "stop_reason": state.stop_reason,
                "status": "completed_noop",
                "reply": None,
                "turn_count": len(ctx.turns),
            }

        sess, replies, final_state = self.run(
            session_id,
            max_steps=max(1, int(additional_steps)),
            run_id=run_id,
            resume=True,
        )
        return {
            "run_id": final_state.run_id,
            "session_id": final_state.session_id,
            "checkpoint_id": final_state.checkpoint_id,
            "loop_index": final_state.loop_index,
            "next_actor": final_state.next_actor,
            "stop_reason": final_state.stop_reason,
            "status": final_state.run_status,
            "reply": replies[-1].model_dump() if replies else None,
            "turn_count": len(sess.turns),
        }

    def list_pending_reviews(self) -> list[dict]:
        return [r.model_dump() for r in self._review_service.list_pending_reviews()]

    def list_reviews(
        self,
        *,
        status: str | None = None,
        session_id: str | None = None,
        topic_id: str | None = None,
    ) -> list[dict]:
        return [
            r.model_dump()
            for r in self._review_service.list_reviews(
                status=status,
                session_id=session_id,
                topic_id=topic_id,
            )
        ]

    def get_review(self, review_id: str) -> dict | None:
        r = self._review_service.get_review(review_id)
        return r.model_dump() if r else None

    def approve_review(
        self,
        review_id: str,
        *,
        action: str = "approve",
        expected_version: int | None = None,
        updated_by: str | None = None,
        payload: dict | None = None,
    ) -> dict:
        status = "approved" if action == "approve" else "rejected"
        item = self._review_service.update_status(
            review_id,
            status=status,
            action=action,
            expected_version=expected_version,
            updated_by=updated_by,
            decision_payload=payload,
        )
        self._event_logger.log(
            run_id=item.run_id,
            session_id=item.session_id,
            backend="v2",
            node_name="review_item_status_changed",
            next_actor=None,
            stop_reason="interrupt_for_review",
            success=True,
            error_summary=None,
            checkpoint_id=item.checkpoint_id,
            quality_decision=item.metadata.get("quality_decision"),
            interrupt_reason=item.interrupt_reason,
            quality_flags=list(item.quality_flags or []),
            review_id=item.review_id,
            policy_id=item.metadata.get("policy_id"),
        )
        return item.model_dump()

    def reject_review(
        self,
        review_id: str,
        *,
        reason: str | None = None,
        expected_version: int | None = None,
        updated_by: str | None = None,
    ) -> dict:
        item = self._review_service.update_status(
            review_id,
            status="rejected",
            action="reject",
            expected_version=expected_version,
            updated_by=updated_by,
            note=reason,
            decision_payload={"reason": reason},
        )
        self._event_logger.log(
            run_id=item.run_id,
            session_id=item.session_id,
            backend="v2",
            node_name="review_item_rejected",
            next_actor=None,
            stop_reason="interrupt_for_review",
            success=True,
            checkpoint_id=item.checkpoint_id,
            interrupt_reason=item.interrupt_reason,
            quality_flags=list(item.quality_flags or []),
            review_id=item.review_id,
            policy_id=item.metadata.get("policy_id"),
        )
        return item.model_dump()

    def resume_from_review(self, review_id: str, *, additional_steps: int = 1) -> dict:
        item = self._review_service.get_review(review_id)
        if item is None:
            raise SessionNotFoundError(f"Review item not found: {review_id}")
        self._review_service.update_status(review_id, status="resumed", action="resume")
        out = self.resume_run(item.session_id, run_id=item.run_id, additional_steps=additional_steps)
        self._review_service.update_status(review_id, status="resolved", action="resolved")
        self._event_logger.log(
            run_id=item.run_id,
            session_id=item.session_id,
            backend="v2",
            node_name="review_resume_completed",
            next_actor=out.get("next_actor"),
            stop_reason=out.get("stop_reason"),
            success=True,
            error_summary=None,
            checkpoint_id=out.get("checkpoint_id"),
            quality_decision=None,
            interrupt_reason=item.interrupt_reason,
            quality_flags=list(item.quality_flags or []),
            review_id=review_id,
            policy_id=item.metadata.get("policy_id"),
        )
        return out

    def apply_edited_draft(
        self,
        review_id: str,
        *,
        edited_text: str,
        expected_version: int | None = None,
        updated_by: str | None = None,
        note: str | None = None,
        resume_after_apply: bool = False,
        additional_steps: int = 1,
    ) -> dict:
        item = self._review_service.apply_edited_draft(
            review_id,
            edited_text=edited_text,
            expected_version=expected_version,
            updated_by=updated_by,
            note=note,
        )
        ctx = self._sessions.manager.load(item.session_id)
        if not ctx:
            raise SessionNotFoundError(item.session_id)
        role = str(item.metadata.get("next_actor") or "assistant")
        turn_id = f"manual-{role}-{len(ctx.turns)+1}"
        ctx.turns.append(
            TranscriptTurn(
                turn_id=turn_id,
                speaker_role=role,
                text=edited_text,
                created_at=self._utc_now_iso(),
                metadata={
                    "manual_override": True,
                    "review_id": review_id,
                    "updated_by": updated_by,
                    "note": note,
                },
            )
        )
        self._sessions.manager.save(ctx)
        item = self._review_service.update_status(
            review_id,
            status="approved",
            action="apply_edited_draft",
            updated_by=updated_by,
            decision_payload={"manual_override_applied": True, "turn_id": turn_id},
            note=note,
        )
        self._event_logger.log(
            run_id=item.run_id,
            session_id=item.session_id,
            backend="v2",
            node_name="review_edited_draft_applied",
            next_actor=role,
            stop_reason="manual_override_applied",
            success=True,
            checkpoint_id=item.checkpoint_id,
            quality_decision=item.metadata.get("quality_decision"),
            interrupt_reason=item.interrupt_reason,
            quality_flags=list(item.quality_flags or []),
            review_id=item.review_id,
            policy_id=item.metadata.get("policy_id"),
        )
        out = {
            "review": item.model_dump(),
            "applied_turn_id": turn_id,
            "turn_count": len(ctx.turns),
        }
        if resume_after_apply:
            self._review_service.update_status(review_id, status="resumed", action="resume_after_apply")
            resume_out = self.resume_run(ctx.session_id, run_id=item.run_id, additional_steps=additional_steps)
            self._review_service.update_status(review_id, status="resolved", action="resolved_after_apply")
            out["resume"] = resume_out
        return out

    def get_review_metrics(self) -> dict:
        items = [x.model_dump() for x in self._review_service.list_reviews()]
        total = len(items)
        pending = sum(1 for i in items if i.get("status") == "pending")
        resolved = sum(1 for i in items if i.get("status") == "resolved")
        manual_override = sum(1 for i in items if (i.get("review_decision_payload") or {}).get("manual_override"))
        interrupted_runs = sum(1 for i in items if i.get("reason") == "quality_interrupt")
        repaired = sum(1 for i in items if (i.get("metadata") or {}).get("quality_decision") == "repair")
        return {
            "created_review_count": total,
            "pending_review_count": pending,
            "resolved_review_count": resolved,
            "interrupt_rate": (interrupted_runs / total) if total else 0.0,
            "repair_rate": (repaired / total) if total else 0.0,
            "manual_override_count": manual_override,
        }
