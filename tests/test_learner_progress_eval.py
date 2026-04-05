from __future__ import annotations

from pathlib import Path

import pytest

from app.evals.loaders import dataset_loader
from app.evals.run_suite import run_eval_suite
from tests.conftest import HAS_SNAPSHOT_V2, SNAPSHOT_V2


@pytest.mark.skipif(not HAS_SNAPSHOT_V2, reason="dev_snapshot_v2 not built")
def test_learner_progress_suite(tmp_path: Path) -> None:
    dataset_loader.reload_cases()
    out = tmp_path / "rep"
    report = run_eval_suite(
        suite_file=Path("tests/fixtures/evals/suites/learner_progress_suite.yaml"),
        snapshot_dir=SNAPSHOT_V2,
        profile_id="default",
        output_dir=out,
    )
    assert report.failed_cases == 0
