"""Aggregate issues from audit + manual fixtures."""

from __future__ import annotations

from pathlib import Path

from app.stability.schemas.consistency import ConsistencyFinding
from app.stability.schemas.issue import IssueRecord
from app.stability.store.issue_store import load_issues_from_path


def findings_to_issues(findings: list[ConsistencyFinding], *, source_type: str = "audit") -> list[IssueRecord]:
    out: list[IssueRecord] = []
    for f in findings:
        if f.passed:
            continue
        sev = f.severity
        if sev not in ("info", "warning", "error", "critical"):
            sev = "warning"
        out.append(
            IssueRecord(
                issue_id=f"audit_{f.finding_id}",
                source_type=source_type,
                severity=sev,
                area="integration",
                title=f"{f.entity_type}:{f.check_type}",
                description=f.message,
                reproducible=True,
                status="open",
                linked_refs=[f.finding_id],
                suggested_fix=f.suggested_fix,
                metadata={"entity_id": f.entity_id},
            )
        )
    return out


def load_manual_issues(known_issues_dir: Path) -> list[IssueRecord]:
    merged: list[IssueRecord] = []
    for name in ("issues.yaml", "manual_issues.yaml"):
        p = known_issues_dir / name
        merged.extend(load_issues_from_path(p))
    return merged


def merge_issues(*batches: list[IssueRecord]) -> list[IssueRecord]:
    seen: set[str] = set()
    out: list[IssueRecord] = []
    for batch in batches:
        for r in batch:
            if r.issue_id in seen:
                continue
            seen.add(r.issue_id)
            out.append(r)
    return out


def summarize_issues(rows: list[IssueRecord]) -> dict[str, object]:
    by_status: dict[str, int] = {}
    by_sev: dict[str, int] = {}
    for r in rows:
        by_status[r.status] = by_status.get(r.status, 0) + 1
        by_sev[r.severity] = by_sev.get(r.severity, 0) + 1
    return {"total": len(rows), "by_status": by_status, "by_severity": by_sev}
