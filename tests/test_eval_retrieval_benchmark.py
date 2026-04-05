"""Retrieval benchmark suite dispatch."""

from __future__ import annotations

from pathlib import Path

import pytest

from app.evals.run_suite import run_eval_suite
from tests.conftest import HAS_SNAPSHOT_V2, SNAPSHOT_V2


@pytest.mark.skipif(not HAS_SNAPSHOT_V2, reason="no dev_snapshot_v2")
def test_retrieval_benchmark_runs(tmp_path: Path) -> None:
    suite = Path("tests/fixtures/evals/suites/retrieval_benchmark.yaml")
    r = run_eval_suite(
        suite_file=suite,
        snapshot_dir=SNAPSHOT_V2,
        profile_id="hybrid_default",
        output_dir=tmp_path / "out",
    )
    assert r.total_cases >= 1
    assert r.passed_cases >= 1
