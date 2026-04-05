from __future__ import annotations

from pathlib import Path

from app.evals.loaders.dataset_loader import reload_cases
from app.evals.run_suite import run_eval_suite
from tests.conftest import HAS_SNAPSHOT_V2, SNAPSHOT_V2


def test_curriculum_delivery_suite(tmp_path: Path) -> None:
    reload_cases()
    if not HAS_SNAPSHOT_V2:
        return
    suite = Path("tests/fixtures/evals/suites/curriculum_delivery_suite.yaml")
    rep = run_eval_suite(
        suite_file=suite,
        snapshot_dir=SNAPSHOT_V2,
        profile_id="default",
        output_dir=tmp_path,
    )
    assert rep.passed_cases == rep.total_cases
