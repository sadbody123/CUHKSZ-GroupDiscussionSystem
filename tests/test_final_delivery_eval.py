"""Final delivery eval suite."""

from __future__ import annotations

from pathlib import Path

import pytest

from app.evals.run_suite import run_eval_suite

PROJECT = Path(__file__).resolve().parents[1]
SUITE = PROJECT / "tests" / "fixtures" / "evals" / "suites" / "final_delivery_suite.yaml"
SNAPSHOT = PROJECT / "app" / "knowledge" / "snapshots" / "dev_snapshot_v2"


@pytest.mark.skipif(not (SNAPSHOT / "manifest.json").is_file(), reason="dev_snapshot_v2 not present")
def test_final_delivery_suite(tmp_path: Path) -> None:
    run_eval_suite(
        suite_file=SUITE,
        snapshot_dir=SNAPSHOT,
        profile_id="v1_demo",
        output_dir=tmp_path / "out",
    )
