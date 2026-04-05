"""Build aggregate StabilityReport."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from app.stability.constants import GREEN, RED, YELLOW
from app.stability.schemas.consistency import ConsistencyFinding
from app.stability.schemas.issue import IssueRecord
from app.stability.schemas.report import StabilityReport
from app.stability.schemas.scenario import E2ERunResult


def build_stability_report(
    *,
    profile_id: str | None,
    findings: list[ConsistencyFinding],
    e2e_results: list[E2ERunResult],
    issues: list[IssueRecord],
    known_limitation_lines: list[str],
) -> StabilityReport:
    now = datetime.now(timezone.utc).isoformat()
    errs = sum(1 for f in findings if not f.passed and f.severity == "error")
    warns = sum(1 for f in findings if not f.passed and f.severity == "warning")
    e2e_fail = sum(1 for r in e2e_results if not r.success)
    if errs > 0 or e2e_fail > 0:
        overall = RED
    elif warns > 0:
        overall = YELLOW
    else:
        overall = GREEN
    crit_open = [i for i in issues if i.severity == "critical" and i.status == "open"]
    actions: list[str] = []
    if crit_open:
        actions.append("Resolve or downgrade critical open issues")
    if errs:
        actions.append("Fix consistency errors (session artifact refs)")
    if e2e_fail:
        actions.append("Re-run failed E2E scenarios with mock provider")
    return StabilityReport(
        report_id=f"sr_{uuid.uuid4().hex[:10]}",
        created_at=now,
        profile_id=profile_id,
        overall_status=overall,
        consistency_summary={"errors": errs, "warnings": warns, "findings": len(findings)},
        e2e_summary={"total": len(e2e_results), "failed": e2e_fail},
        issue_summary={"open_critical": len(crit_open), "total_tracked": len(issues)},
        known_limitations=list(known_limitation_lines),
        recommended_actions=actions,
        metadata={},
    )
