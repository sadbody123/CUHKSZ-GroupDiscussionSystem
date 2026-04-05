"""Lineage metadata for drafts and publications."""

from __future__ import annotations

from typing import Any


def build_lineage(
    *,
    base_artifact_ref_id: str | None,
    derivative_of: str | None,
    draft_id: str,
    publication_chain: list[str] | None = None,
    patch_source_refs: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "draft_id": draft_id,
        "base_artifact_ref_id": base_artifact_ref_id,
        "derivative_of": derivative_of,
        "publication_chain": list(publication_chain or []),
        "patch_source_refs": list(patch_source_refs or []),
    }
