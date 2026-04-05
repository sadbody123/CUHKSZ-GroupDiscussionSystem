"""Persist group balance reports."""

from __future__ import annotations

import json
from pathlib import Path

from app.group_sim.schemas.report import GroupBalanceReport


class GroupReportStore:
    def __init__(self, root: Path) -> None:
        self._root = root.resolve()
        self._root.mkdir(parents=True, exist_ok=True)

    def save(self, report: GroupBalanceReport) -> Path:
        p = self._root / f"{report.session_id}_{report.report_id}.json"
        p.write_text(json.dumps(report.model_dump(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return p

    def load_by_session(self, session_id: str) -> GroupBalanceReport | None:
        if not self._root.is_dir():
            return None
        for p in sorted(self._root.glob(f"{session_id}_*.json"), reverse=True):
            try:
                raw = json.loads(p.read_text(encoding="utf-8"))
                return GroupBalanceReport.model_validate(raw)
            except Exception:
                continue
        return None
