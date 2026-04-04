"""Markdown report."""

from __future__ import annotations

from pathlib import Path

from app.evals.schemas.report import EvalReport


def write(path: Path, report: EvalReport) -> None:
    lines = [
        f"# Eval report: {report.suite_id or 'adhoc'}",
        "",
        f"- Created: {report.created_at}",
        f"- Profiles: {', '.join(report.profile_ids)}",
        f"- Passed: {report.passed_cases} / {report.total_cases}",
        "",
        "## Cases",
        "",
    ]
    for r in report.results:
        st = "PASS" if r.get("passed") else "FAIL"
        lines.append(f"- **{r.get('case_id')}** ({r.get('case_type')}) — {st}")
        if not r.get("passed") and r.get("details"):
            lines.append(f"  - details: `{r.get('details')}`")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
