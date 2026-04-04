"""Run an eval suite and build a report."""

from __future__ import annotations

import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path

from app.evals.loaders.dataset_loader import load_case
from app.evals.loaders.suite_loader import load_suite
from app.evals.reporters import csv_reporter, json_reporter, markdown_reporter
from app.evals.runners import agent_runner, analyzer_runner, e2e_runner, retrieval_runner, state_machine_runner
from app.evals.schemas.report import EvalReport


def _dispatch(case_type: str):
    return {
        "retrieval_case": retrieval_runner.run_retrieval_case,
        "state_machine_case": state_machine_runner.run_state_machine_case,
        "analyzer_case": analyzer_runner.run_analyzer_case,
        "agent_case": agent_runner.run_agent_case,
        "e2e_case": e2e_runner.run_e2e_case,
    }.get(case_type)


def run_eval_suite(
    *,
    suite_file: Path,
    snapshot_dir: Path,
    profile_id: str,
    output_dir: Path,
) -> EvalReport:
    suite = load_suite(suite_file)
    prof = profile_id or suite.default_runtime_profile_id or "default"
    output_dir.mkdir(parents=True, exist_ok=True)
    results: list[dict] = []
    with tempfile.TemporaryDirectory() as tdir:
        tmp = Path(tdir)
        for ref in suite.case_refs:
            case = load_case(ref)
            fn = _dispatch(case.case_type)
            if not fn:
                raise ValueError(f"Unknown case_type: {case.case_type}")
            if case.case_type == "e2e_case":
                r = fn(case, snapshot_dir, prof, tmp)
            else:
                r = fn(case, snapshot_dir, prof)
            row = r.model_dump()
            row["profile_id"] = prof
            results.append(row)

    passed = sum(1 for x in results if x.get("passed"))
    report = EvalReport(
        report_id=str(uuid.uuid4()),
        created_at=datetime.now(timezone.utc).isoformat(),
        suite_id=suite.suite_id,
        profile_ids=[prof],
        total_cases=len(results),
        passed_cases=passed,
        failed_cases=len(results) - passed,
        summary={"suite": suite.suite_id, "profile": prof},
        results=results,
        metadata={},
    )
    json_reporter.write(output_dir / "report.json", report)
    markdown_reporter.write(output_dir / "report.md", report)
    csv_reporter.write(output_dir / "report.csv", report)
    return report


def compare_profiles(
    *,
    suite_file: Path,
    snapshot_dir: Path,
    profiles: list[str],
    output_dir: Path,
) -> EvalReport:
    """Run the same suite for multiple profiles; aggregate one report."""
    output_dir.mkdir(parents=True, exist_ok=True)
    all_results: list[dict] = []
    suite = load_suite(suite_file)
    for pid in profiles:
        sub = output_dir / pid
        r = run_eval_suite(suite_file=suite_file, snapshot_dir=snapshot_dir, profile_id=pid, output_dir=sub)
        for row in r.results:
            row = {**row, "profile_id": pid}
            all_results.append(row)
    passed = sum(1 for x in all_results if x.get("passed"))
    report = EvalReport(
        report_id=str(uuid.uuid4()),
        created_at=datetime.now(timezone.utc).isoformat(),
        suite_id=suite.suite_id,
        profile_ids=list(profiles),
        total_cases=len(all_results),
        passed_cases=passed,
        failed_cases=len(all_results) - passed,
        summary={"mode": "compare_profiles", "profiles": profiles},
        results=all_results,
        metadata={},
    )
    json_reporter.write(output_dir / "report.json", report)
    markdown_reporter.write(output_dir / "report.md", report)
    csv_reporter.write(output_dir / "report.csv", report)
    return report
