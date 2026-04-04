"""E2E eval runner."""

from __future__ import annotations

import pytest

from app.evals.loaders.dataset_loader import load_case, reload_cases
from app.evals.runners import e2e_runner
from tests.conftest import HAS_SNAPSHOT_V2, SNAPSHOT_V2


@pytest.mark.skipif(not HAS_SNAPSHOT_V2, reason="no snapshot")
def test_sm_e2e(tmp_path):
    reload_cases()
    case = load_case("smoke_e2e")
    r = e2e_runner.run_e2e_case(case, SNAPSHOT_V2, "default", tmp_path)
    assert r.passed
