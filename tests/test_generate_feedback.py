"""Coach feedback generation."""

from __future__ import annotations

from pathlib import Path

import pytest

from app.runtime.execution.feedback_runner import run_generate_feedback
from app.runtime.execution.turn_executor import TurnExecutor
from app.runtime.schemas.session import SessionContext
from app.runtime.snapshot_loader import load_snapshot
from app.runtime.session.manager import SessionManager
from app.runtime.session.file_store import FileSessionStore
from tests.conftest import HAS_SNAPSHOT_V2


@pytest.mark.skipif(not HAS_SNAPSHOT_V2, reason="no snapshot")
def test_generate_feedback_report(tmp_path: Path, snapshot_v2_dir: Path):
    b = load_snapshot(snapshot_v2_dir)
    ctx = SessionContext(
        session_id="fb",
        topic_id="tc-campus-ai",
        phase="discussion",
        provider_name="mock",
        snapshot_dir=str(snapshot_v2_dir.resolve()),
    )
    ex = TurnExecutor(b, ctx)
    ex.submit_user_turn("I agree. For example, we can use AI to outline ideas.")
    mgr = SessionManager(FileSessionStore(tmp_path))
    report = run_generate_feedback(ex, mgr)
    assert report.text
    assert report.feedback_packet
