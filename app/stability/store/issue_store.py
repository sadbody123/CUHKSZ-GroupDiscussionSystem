"""Load issue fixtures from disk."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from app.stability.schemas.issue import IssueRecord


def load_issues_from_path(path: Path) -> list[IssueRecord]:
    if not path.is_file():
        return []
    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    out: list[IssueRecord] = []
    for row in raw.get("issues", []) or []:
        out.append(IssueRecord.model_validate(row))
    return out


def merge_issue_dicts(rows: list[dict[str, Any]]) -> list[IssueRecord]:
    return [IssueRecord.model_validate(r) for r in rows]
