"""Group simulation eval suite."""

from __future__ import annotations

from pathlib import Path

import pytest

from app.evals.loaders.dataset_loader import reload_cases
from app.evals.run_suite import run_eval_suite

from tests.conftest import HAS_SNAPSHOT_V2, SNAPSHOT_V2


@pytest.mark.skipif(not HAS_SNAPSHOT_V2, reason="needs dev_snapshot_v2")
def test_group_simulation_suite(tmp_path: Path) -> None:
    reload_cases()
    report = run_eval_suite(
        suite_file=Path("tests/fixtures/evals/suites/group_simulation_suite.yaml"),
        snapshot_dir=SNAPSHOT_V2,
        profile_id="default",
        output_dir=tmp_path / "out",
    )
    assert report.failed_cases == 0
