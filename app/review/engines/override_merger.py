"""Merge approved human overrides into reviewed output artifacts."""

from __future__ import annotations

import copy
import uuid
from datetime import datetime, timezone
from typing import Any

from app.review.constants import PROXY_DISCLAIMER_NOTE
from app.review.schemas.override import OverrideDecision
from app.review.schemas.report import ReviewedOutputArtifact


def _navigate(parent: dict[str, Any], parts: list[str]) -> dict[str, Any] | None:
    cur: Any = parent
    for p in parts[:-1]:
        if not isinstance(cur, dict) or p not in cur:
            return None
        cur = cur[p]
        if not isinstance(cur, dict):
            return None
    return cur if isinstance(cur, dict) else None


def _apply(parent: dict[str, Any], path: str, value: Any, action: str) -> None:
    parts = [p for p in path.split(".") if p]
    if not parts:
        return
    leaf = parts[-1]
    node = _navigate(parent, parts)
    if node is None:
        return
    if action == "replace":
        node[leaf] = value
    elif action == "append":
        cur = node.get(leaf)
        if isinstance(cur, list):
            node[leaf] = cur + (value if isinstance(value, list) else [value])
        elif isinstance(cur, str) and isinstance(value, str):
            node[leaf] = cur + "\n" + value
        else:
            node[leaf] = value
    elif action == "suppress":
        node[leaf] = None
    elif action == "mark_uncertain":
        node[leaf] = {"uncertain": True, "hint": value}


def merge_reviewed_feedback(
    *,
    base_coach_report: dict[str, Any] | None,
    overrides: list[OverrideDecision],
    review_id: str,
    reviewer_id: str,
    review_pack_id: str,
    session_id: str,
) -> ReviewedOutputArtifact:
    """Apply approved overrides to a deep copy of coach_report-shaped payload."""
    payload: dict[str, Any] = copy.deepcopy(base_coach_report) if base_coach_report else {}
    for ov in overrides:
        if not ov.approved:
            continue
        if ov.target_type not in (
            "feedback",
            "coach_report",
            "session",
            "speech_report",
            "group_report",
            "learner_report",
            "mode_report",
        ):
            continue
        _apply(payload, ov.target_path, ov.new_value, ov.action)

    now = datetime.now(timezone.utc).isoformat()
    return ReviewedOutputArtifact(
        artifact_kind="reviewed_feedback",
        review_id=review_id,
        reviewer_id=reviewer_id,
        review_pack_id=review_pack_id,
        session_id=session_id,
        created_at=now,
        source="human_review_merge",
        proxy_note=PROXY_DISCLAIMER_NOTE,
        payload=payload,
        metadata={
            "override_ids": [o.override_id for o in overrides if o.approved],
            "merge_id": str(uuid.uuid4()),
        },
    )
