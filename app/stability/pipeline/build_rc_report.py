"""Pipeline: build RC report from inputs."""

from __future__ import annotations

from app.stability.engines.rc_gate import build_rc_report
from app.stability.schemas.issue import IssueRecord

# re-export for CLI
__all__ = ["build_rc_report", "IssueRecord"]
