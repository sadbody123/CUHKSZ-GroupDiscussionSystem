from __future__ import annotations

from pathlib import Path

from app.learner.store.file_store import LearnerFileStore


def test_learner_file_store_roundtrip(tmp_path: Path) -> None:
    store = LearnerFileStore(tmp_path / "learners")
    p = store.create_learner("t1", display_name="Test")
    assert p.learner_id == "t1"
    loaded = store.load_learner_profile("t1")
    assert loaded is not None
    assert loaded.display_name == "Test"
    assert store.list_learners() == ["t1"]
