from __future__ import annotations

from pathlib import Path

from app.review.schemas.reviewer import ReviewerProfile
from app.review.store.reviewer_store import ReviewerStore


def test_reviewer_roundtrip(tmp_path: Path) -> None:
    st = ReviewerStore(tmp_path)
    p = ReviewerProfile(
        reviewer_id="r1",
        display_name="T",
        created_at="2026-01-01T00:00:00Z",
    )
    st.save_reviewer(p)
    loaded = st.load_reviewer("r1")
    assert loaded and loaded.display_name == "T"
