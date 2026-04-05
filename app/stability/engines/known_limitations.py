"""Accepted limitations vs open issues."""

from __future__ import annotations

from app.stability.schemas.issue import IssueRecord


def accepted_limitation_lines(rows: list[IssueRecord]) -> list[str]:
    out: list[str] = []
    for r in rows:
        if r.status != "accepted_limitation":
            continue
        reason = r.metadata.get("reason") or r.description or r.title
        out.append(f"- [{r.issue_id}] {r.title}: {reason}")
    return out


def filter_known_issues_for_api(rows: list[IssueRecord]) -> list[dict]:
    """Do not leak file paths in metadata."""
    out: list[dict] = []
    for r in rows:
        md = {k: v for k, v in (r.metadata or {}).items() if not k.endswith("_path")}
        out.append({**r.model_dump(), "metadata": md})
    return out
