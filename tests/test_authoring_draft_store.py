from __future__ import annotations

from app.authoring.schemas.draft import AuthoringDraft
from app.authoring.store.draft_store import DraftStore


def test_draft_roundtrip(tmp_path) -> None:
    ds = DraftStore(tmp_path / "drafts")
    d = AuthoringDraft(
        draft_id="d1",
        artifact_type="curriculum_pack",
        artifact_id="x",
        status="draft",
        created_at="2026-01-01T00:00:00Z",
        content={"pack_id": "custom1", "display_name": "X", "steps": []},
    )
    ds.create_draft(d)
    d2 = ds.load_draft("d1")
    assert d2 and d2.draft_id == "d1"
