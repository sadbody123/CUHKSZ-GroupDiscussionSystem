from __future__ import annotations

from pathlib import Path

from app.evals.loaders.dataset_loader import reload_cases
from app.evals.run_suite import run_eval_suite


def test_authoring_publication_suite(tmp_path: Path) -> None:
    reload_cases()
    suite = Path("tests/fixtures/evals/suites/authoring_publication_suite.yaml")
    rep = run_eval_suite(
        suite_file=suite,
        snapshot_dir=Path("."),
        profile_id="default",
        output_dir=tmp_path,
    )
    assert rep.passed_cases == rep.total_cases
