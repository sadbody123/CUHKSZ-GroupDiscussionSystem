"""Optional links to reviewed artifacts (references only)."""

from __future__ import annotations

from typing import Any


def merge_review_refs_into_pack_metadata(metadata: dict[str, Any], reviewed_refs: list[str]) -> dict[str, Any]:
    out = dict(metadata)
    if reviewed_refs:
        out["linked_reviewed_artifact_refs"] = reviewed_refs
    return out
