"""State machine eval runner."""

from __future__ import annotations

import pytest

from app.evals.loaders.dataset_loader import load_case, reload_cases
from app.evals.runners import state_machine_runner
from tests.conftest import HAS_SNAPSHOT_V2, SNAPSHOT_V2


@pytest.mark.skipif(not HAS_SNAPSHOT_V2, reason="no snapshot")
def test_sm_state_machine():
    reload_cases()
    case = load_case("smoke_state_machine")
    r = state_machine_runner.run_state_machine_case(case, SNAPSHOT_V2, "default")
    assert r.passed
    assert r.details.get("next_role") == "user"
