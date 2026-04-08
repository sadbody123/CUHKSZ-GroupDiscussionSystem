"""Application-friendly runtime V2 review queue service."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from app.agent_runtime_v2.review.schemas import ReviewItem
from app.agent_runtime_v2.review.store import ReviewQueueStore


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class RuntimeReviewService:
    def __init__(self, store: ReviewQueueStore) -> None:
        self._store = store

    def create_item(
        self,
        *,
        session_id: str,
        run_id: str,
        checkpoint_id: str | None,
        topic_id: str | None,
        reason: str | None,
        interrupt_reason: str | None,
        quality_flags: list[str],
        draft_reply_text: str | None,
        draft_reply_summary: str | None,
        metadata: dict | None = None,
    ) -> ReviewItem:
        now = _utc_now_iso()
        item = ReviewItem(
            review_id=f"rvw-{uuid4()}",
            session_id=session_id,
            run_id=run_id,
            checkpoint_id=checkpoint_id,
            topic_id=topic_id,
            reason=reason,
            interrupt_reason=interrupt_reason,
            quality_flags=list(quality_flags or []),
            draft_reply_text=draft_reply_text,
            draft_reply_summary=draft_reply_summary,
            status="pending",
            version=1,
            allowed_actions=["approve", "reject", "resume", "apply_edited_draft"],
            created_at=now,
            updated_at=now,
            metadata=dict(metadata or {}),
        )
        self._store.save(item)
        return item

    def list_pending_reviews(self) -> list[ReviewItem]:
        return self._store.list(status="pending")

    def list_reviews(
        self,
        *,
        status: str | None = None,
        session_id: str | None = None,
        topic_id: str | None = None,
    ) -> list[ReviewItem]:
        return self._store.list(status=status, session_id=session_id, topic_id=topic_id)

    def get_review(self, review_id: str) -> ReviewItem | None:
        return self._store.load(review_id)

    @staticmethod
    def _allowed_actions_for_status(status: str) -> list[str]:
        if status == "pending":
            return ["approve", "reject", "resume", "apply_edited_draft"]
        if status == "approved":
            return ["resume", "resolve"]
        if status == "resumed":
            return ["resolve"]
        return []

    @staticmethod
    def _is_transition_valid(current: str, target: str) -> bool:
        valid = {
            "pending": {"approved", "rejected", "resumed", "resolved"},
            "approved": {"resumed", "resolved"},
            "rejected": {"resolved"},
            "resumed": {"resolved"},
            "resolved": set(),
        }
        return target in valid.get(current, set())

    def update_status(
        self,
        review_id: str,
        *,
        status: str,
        action: str | None = None,
        expected_version: int | None = None,
        updated_by: str | None = None,
        decision_payload: dict | None = None,
        note: str | None = None,
    ) -> ReviewItem:
        item = self._store.load(review_id)
        if item is None:
            raise ValueError(f"review not found: {review_id}")
        if expected_version is not None and int(item.version) != int(expected_version):
            raise ValueError("review version conflict")
        if not self._is_transition_valid(item.status, status):
            raise ValueError(f"invalid status transition: {item.status} -> {status}")
        item.status = status
        item.version += 1
        item.updated_at = _utc_now_iso()
        item.updated_by = updated_by
        if status in {"approved", "rejected", "resolved"}:
            item.resolved_by = updated_by
        item.allowed_actions = self._allowed_actions_for_status(status)
        if action:
            item.metadata = {**item.metadata, "last_action": action}
        if decision_payload:
            item.review_decision_payload = {**item.review_decision_payload, **decision_payload}
        if note:
            item.notes = [*item.notes, note]
        self._store.save(item)
        return item

    def apply_edited_draft(
        self,
        review_id: str,
        *,
        edited_text: str,
        expected_version: int | None = None,
        updated_by: str | None = None,
        note: str | None = None,
    ) -> ReviewItem:
        item = self._store.load(review_id)
        if item is None:
            raise ValueError(f"review not found: {review_id}")
        if item.status != "pending":
            raise ValueError(f"cannot edit draft when status={item.status}")
        if expected_version is not None and int(item.version) != int(expected_version):
            raise ValueError("review version conflict")
        item.draft_reply_text = edited_text
        item.draft_reply_summary = edited_text[:500]
        item.version += 1
        item.updated_at = _utc_now_iso()
        item.updated_by = updated_by
        item.allowed_actions = self._allowed_actions_for_status(item.status)
        item.review_decision_payload = {
            **item.review_decision_payload,
            "manual_override": True,
            "edited_draft": True,
        }
        if note:
            item.notes = [*item.notes, note]
        self._store.save(item)
        return item
