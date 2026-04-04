"""Analyzer eval runner."""

from __future__ import annotations

import pytest

from app.evals.loaders.dataset_loader import load_case, reload_cases
from app.evals.runners import analyzer_runner
from tests.conftest import HAS_SNAPSHOT_V2, SNAPSHOT_V2


@pytest.mark.skipif(not HAS_SNAPSHOT_V2, reason="no snapshot")
def test_sm_analyzer():
    reload_cases()
    case = load_case("smoke_analyzer")
    r = analyzer_runner.run_analyzer_case(case, SNAPSHOT_V2, "default")
    assert r.passed
