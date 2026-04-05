"""Eval suite for practice modes (requires local dev_snapshot_v2)."""

from __future__ import annotations

from pathlib import Path

import pytest

from app.evals.loaders.dataset_loader import reload_cases
from app.evals.run_suite import run_eval_suite

from tests.conftest import HAS_SNAPSHOT_V2, SNAPSHOT_V2


@pytest.mark.skipif(not HAS_SNAPSHOT_V2, reason="needs app/knowledge/snapshots/dev_snapshot_v2")
def test_mode_and_assessment_suite_passes(tmp_path: Path) -> None:
    reload_cases()
    out = tmp_path / "mode_eval_out"
    report = run_eval_suite(
        suite_file=Path("tests/fixtures/evals/suites/mode_and_assessment_suite.yaml"),
        snapshot_dir=SNAPSHOT_V2,
        profile_id="default",
        output_dir=out,
    )
    assert report.failed_cases == 0, report.results
