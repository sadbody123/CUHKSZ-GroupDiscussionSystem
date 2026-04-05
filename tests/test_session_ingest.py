from __future__ import annotations

from pathlib import Path

from app.learner.aggregation.session_ingest import SessionIngestor
from app.learner.store.file_store import LearnerFileStore
from app.runtime.schemas.session import SessionContext
from app.runtime.session.file_store import FileSessionStore
from app.runtime.session.manager import SessionManager


def test_ingest_updates_timeline(tmp_path: Path) -> None:
    sess_dir = tmp_path / "sessions"
    learn_dir = tmp_path / "learners"
    speech_dir = tmp_path / "speech"
    snap = tmp_path / "snap"
    snap.mkdir()
    (snap / "manifest.json").write_text('{"snapshot_id":"s1","schema_version":"1"}\n', encoding="utf-8")

    fixture = Path(__file__).parent / "fixtures/learners/session_exports/learner_fixture_sess_01.json"
    data = fixture.read_text(encoding="utf-8")
    ctx = SessionContext.model_validate_json(data)
    ctx.snapshot_dir = str(snap)

    store = LearnerFileStore(learn_dir)
    store.create_learner("L1", display_name="T")
    mgr = SessionManager(FileSessionStore(sess_dir))
    mgr.save(ctx)

    ing = SessionIngestor(store, mgr, speech_report_dir=speech_dir)
    ing.ingest("L1", ctx.session_id, skip_if_duplicate=False)
    tl = store.load_timeline("L1")
    assert len(tl) == 1
