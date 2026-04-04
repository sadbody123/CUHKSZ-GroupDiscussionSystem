"""Session manager + file store."""

from __future__ import annotations

from pathlib import Path

from app.runtime.session.file_store import FileSessionStore
from app.runtime.session.manager import SessionManager


def test_create_load_save(tmp_path: Path):
    store = FileSessionStore(tmp_path / "sess")
    mgr = SessionManager(store)
    ctx = mgr.create_session(
        topic_id="tc-campus-ai",
        snapshot_dir="/tmp/snap",
        provider_name="mock",
    )
    assert ctx.session_id
    loaded = mgr.load(ctx.session_id)
    assert loaded and loaded.topic_id == "tc-campus-ai"
    loaded.phase = "summary"
    mgr.save(loaded)
    again = mgr.load(ctx.session_id)
    assert again and again.phase == "summary"
