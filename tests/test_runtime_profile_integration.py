"""Session + executor use runtime profile."""

from __future__ import annotations

import pytest

from app.runtime.execution.turn_executor import TurnExecutor
from app.runtime.schemas.session import SessionContext
from app.runtime.snapshot_loader import load_snapshot
from tests.conftest import HAS_SNAPSHOT_V2, SNAPSHOT_V2


@pytest.mark.skipif(not HAS_SNAPSHOT_V2, reason="no snapshot")
def test_turn_executor_resolves_profile():
    ctx = SessionContext(
        session_id="x",
        topic_id="tc-campus-ai",
        phase="discussion",
        snapshot_dir=str(SNAPSHOT_V2),
        provider_name="mock",
        runtime_profile_id="concise",
    )
    ex = TurnExecutor(load_snapshot(SNAPSHOT_V2), ctx)
    assert ex.profile.profile_id == "concise"
    assert ex.sm._orch.get("discussion_turn_threshold", 12) == 10
