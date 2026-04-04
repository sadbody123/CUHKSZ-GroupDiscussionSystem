"""Session replay."""

from __future__ import annotations

import pytest

from app.evals.replay.engine import replay_analyze
from tests.conftest import HAS_SNAPSHOT_V2, PROJECT_ROOT, SNAPSHOT_V2


@pytest.mark.skipif(not HAS_SNAPSHOT_V2, reason="no snapshot")
def test_replay_analyze():
    p = PROJECT_ROOT / "tests" / "fixtures" / "evals" / "sessions" / "sample_session_export.json"
    out = replay_analyze(p, "strict_coach", SNAPSHOT_V2)
    assert "signals" in out
