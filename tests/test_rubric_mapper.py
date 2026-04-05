from __future__ import annotations

from app.review.engines.rubric_mapper import build_rubric_dimensions_for_snapshot
from tests.conftest import SNAPSHOT_V2, HAS_SNAPSHOT_V2


def test_rubric_fallback_or_snapshot() -> None:
    dims = build_rubric_dimensions_for_snapshot(SNAPSHOT_V2 if HAS_SNAPSHOT_V2 else None)
    assert len(dims) >= 1
    # Either pedagogy-derived ids (e.g. pedagogy_*) or fallback includes "content"
    assert any("content" in d.dimension_id for d in dims) or any(d.source == "pedagogy" for d in dims)
