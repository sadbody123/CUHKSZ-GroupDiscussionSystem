"""Release finalization eval suite (phase 17)."""

from __future__ import annotations

from pathlib import Path

import pytest

from app.evals.loaders.dataset_loader import reload_cases
from app.evals.run_suite import run_eval_suite

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SUITE = PROJECT_ROOT / "tests" / "fixtures" / "evals" / "suites" / "release_finalization_suite.yaml"
SNAPSHOT = PROJECT_ROOT / "app" / "knowledge" / "snapshots" / "dev_snapshot_v2"


@pytest.mark.skipif(not (SNAPSHOT / "manifest.json").is_file(), reason="dev_snapshot_v2 not built")
def test_release_finalization_suite(tmp_path: Path) -> None:
    reload_cases()
    out = tmp_path / "release_eval"
    r = run_eval_suite(suite_file=SUITE, snapshot_dir=SNAPSHOT, profile_id="v1_demo", output_dir=out)
    assert r.failed_cases == 0, r.results
