"""Pipeline: submit human review and optional merge."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from app.review.config import ReviewConfig
from app.review.constants import PACK_SUBMITTED
from app.review.engines.acceptance_policy import can_submit
from app.review.engines.override_merger import merge_reviewed_feedback
from app.review.engines.review_queue import on_pack_submitted
from app.review.schemas.override import OverrideDecision
from app.review.schemas.report import HumanReview
from app.review.store.queue_index import QueueIndex
from app.review.store.reviewer_store import ReviewerStore
from app.review.store.review_store import ReviewStore


def human_review_from_payload(data: dict[str, Any], *, review_pack_id: str, reviewer_id: str) -> HumanReview:
    now = datetime.now(timezone.utc).isoformat()
    return HumanReview(
        review_id=str(uuid.uuid4()),
        review_pack_id=review_pack_id,
        reviewer_id=reviewer_id,
        created_at=now,
        rubric_scores=list(data.get("rubric_scores") or []),
        annotations=list(data.get("annotations") or []),
        override_decisions=list(data.get("override_decisions") or []),
        overall_judgment=data.get("overall_judgment"),
        summary_notes=list(data.get("summary_notes") or []),
        metadata=dict(data.get("metadata") or {}),
    )


def run_submit_review(
    *,
    review_pack_id: str,
    reviewer_id: str,
    payload: dict[str, Any],
    review_store: ReviewStore,
    reviewer_store: ReviewerStore,
    queue: QueueIndex | None,
    cfg: ReviewConfig,
    coach_report: dict | None,
) -> HumanReview:
    pack = review_store.load_review_pack(review_pack_id)
    rev = reviewer_store.load_reviewer(reviewer_id)
    hr = human_review_from_payload(payload, review_pack_id=review_pack_id, reviewer_id=reviewer_id)
    can_submit(pack=pack, reviewer=rev, hr=hr)
    review_store.save_human_review(hr)
    if pack:
        pack.status = PACK_SUBMITTED
        pack.metadata = {**pack.metadata, "last_review_id": hr.review_id}
        review_store.save_review_pack(pack)
    if queue and pack:
        on_pack_submitted(queue, review_pack_id, pack.session_id)
    if cfg.enable_override_merge and coach_report is not None and pack:
        ods = []
        for x in hr.override_decisions:
            if isinstance(x, dict):
                try:
                    ods.append(OverrideDecision.model_validate(x))
                except Exception:
                    continue
        artifact = merge_reviewed_feedback(
            base_coach_report=coach_report,
            overrides=ods,
            review_id=hr.review_id,
            reviewer_id=reviewer_id,
            review_pack_id=review_pack_id,
            session_id=pack.session_id,
        )
        review_store.save_reviewed_output(artifact)
    return hr
