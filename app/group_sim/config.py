"""Resolve roster template asset paths."""

from __future__ import annotations

from pathlib import Path

from app.ops.settings import get_ops_settings


def roster_template_dir() -> Path:
    s = get_ops_settings()
    rd = getattr(s, "roster_template_dir", None)
    if rd:
        return Path(rd).resolve()
    return Path(__file__).resolve().parent / "roster_templates"


def group_reports_dir() -> Path:
    s = get_ops_settings()
    return Path(s.group_reports_dir).resolve()
