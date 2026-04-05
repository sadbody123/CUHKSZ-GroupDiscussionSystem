"""Release candidate go / no-go from readiness + stability signals."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from app.stability.constants import CONDITIONAL_GO, GO, NO_GO
from app.stability.schemas.issue import IssueRecord
from app.stability.schemas.rc import ReleaseCandidateReport


def build_rc_report(
    *,
    profile_id: str,
    readiness_status: str,
    stability_overall: str,
    open_issues: list[IssueRecord],
    e2e_all_success: bool,
    consistency_failed_errors: int,
) -> ReleaseCandidateReport:
    now = datetime.now(timezone.utc).isoformat()
    blocking = [i.issue_id for i in open_issues if i.severity == "critical" and i.status == "open"]
    accepted = [
        f"{i.issue_id}: {i.title}"
        for i in open_issues
        if i.status == "accepted_limitation"
    ]

    gating = [
        {"check": "readiness", "passed": readiness_status != "blocked", "detail": readiness_status},
        {"check": "stability", "passed": stability_overall != "red", "detail": stability_overall},
        {"check": "e2e_matrix", "passed": e2e_all_success, "detail": "all scenarios succeeded"},
        {"check": "consistency_errors", "passed": consistency_failed_errors == 0, "detail": str(consistency_failed_errors)},
    ]

    if readiness_status == "blocked" or blocking:
        go = NO_GO
    elif stability_overall == "red" or not e2e_all_success or consistency_failed_errors > 0:
        go = CONDITIONAL_GO
    else:
        go = GO

    return ReleaseCandidateReport(
        rc_report_id=f"rc_{uuid.uuid4().hex[:10]}",
        profile_id=profile_id,
        created_at=now,
        readiness_status=readiness_status,
        gating_checks=gating,
        blocking_issue_ids=blocking,
        accepted_limitations=accepted,
        demo_matrix_summary={"e2e_all_success": e2e_all_success},
        stability_summary={"overall": stability_overall},
        docs_status={"stub": True},
        go_no_go=go,
        metadata={},
    )


def stability_overall_from_signals(
    *,
    consistency_errors: int,
    consistency_warnings: int,
    e2e_failed: int,
) -> str:
    from app.stability.constants import GREEN, RED, YELLOW

    if consistency_errors > 0 or e2e_failed > 0:
        return RED
    if consistency_warnings > 0:
        return YELLOW
    return GREEN
