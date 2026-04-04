"""Turn executor and auto loop."""

from __future__ import annotations

from pathlib import Path

import pytest

from app.runtime.execution.discussion_loop import auto_run_discussion
from app.runtime.execution.turn_executor import TurnExecutor
from app.runtime.schemas.session import SessionContext
from app.runtime.snapshot_loader import load_snapshot
from tests.conftest import HAS_SNAPSHOT_V2


@pytest.mark.skipif(not HAS_SNAPSHOT_V2, reason="no snapshot")
def test_run_next_turn_updates_transcript(snapshot_v2_dir: Path):
    b = load_snapshot(snapshot_v2_dir)
    ctx = SessionContext(
        session_id="exec-test",
        topic_id="tc-campus-ai",
        phase="discussion",
        provider_name="mock",
        snapshot_dir=str(snapshot_v2_dir.resolve()),
    )
    ex = TurnExecutor(b, ctx)
    ex.submit_user_turn("Opening statement for discussion.")
    ctx2, reply = ex.run_next_turn()
    assert reply is not None
    assert len(ctx2.turns) >= 2


@pytest.mark.skipif(not HAS_SNAPSHOT_V2, reason="no snapshot")
def test_auto_run(snapshot_v2_dir: Path):
    b = load_snapshot(snapshot_v2_dir)
    ctx = SessionContext(
        session_id="auto",
        topic_id="tc-campus-ai",
        phase="discussion",
        provider_name="mock",
        snapshot_dir=str(snapshot_v2_dir.resolve()),
    )
    ex = TurnExecutor(b, ctx)
    ex.submit_user_turn("start")
    sess, reps = auto_run_discussion(ex, max_steps=2, auto_fill_user=True)
    assert len(reps) >= 1
