"""Eval reporters."""

from __future__ import annotations

from pathlib import Path

from app.evals.reporters import csv_reporter, json_reporter, markdown_reporter
from app.evals.schemas.report import EvalReport


def test_reporters_write(tmp_path: Path):
    r = EvalReport(
        report_id="r1",
        created_at="t",
        suite_id="s",
        profile_ids=["default"],
        total_cases=1,
        passed_cases=1,
        failed_cases=0,
        results=[{"case_id": "c1", "case_type": "x", "passed": True, "score": 1.0, "profile_id": "default"}],
    )
    json_reporter.write(tmp_path / "a.json", r)
    markdown_reporter.write(tmp_path / "a.md", r)
    csv_reporter.write(tmp_path / "a.csv", r)
    assert (tmp_path / "a.json").is_file()
