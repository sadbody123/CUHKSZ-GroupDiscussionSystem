from __future__ import annotations

from pathlib import Path

from app.evals.run_suite import run_eval_suite
from tests.conftest import SNAPSHOT_V2, HAS_SNAPSHOT_V2


def test_review_calibration_suite(tmp_path: Path) -> None:
    if not HAS_SNAPSHOT_V2:
        return
    suite = Path("tests/fixtures/evals/suites/review_calibration_suite.yaml")
    rep = run_eval_suite(
        suite_file=suite,
        snapshot_dir=SNAPSHOT_V2,
        profile_id="default",
        output_dir=tmp_path,
    )
    assert rep.passed_cases == rep.total_cases
