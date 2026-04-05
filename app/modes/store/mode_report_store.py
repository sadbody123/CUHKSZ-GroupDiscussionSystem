"""Persist ModeSessionReport JSON."""

from __future__ import annotations

import json
import re
from pathlib import Path

from app.modes.schemas.report import ModeSessionReport

_SAFE = re.compile(r"^[\w.\-]+$")


class ModeReportStore:
    def __init__(self, root: Path) -> None:
        self._root = root.resolve()
        self._root.mkdir(parents=True, exist_ok=True)

    def save(self, report: ModeSessionReport) -> Path:
        if not _SAFE.match(report.session_id):
            raise ValueError("invalid session_id")
        p = self._root / f"{report.session_id}_{report.report_id}.json"
        p.write_text(json.dumps(report.model_dump(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return p

    def load_by_session(self, session_id: str) -> ModeSessionReport | None:
        if not self._root.is_dir():
            return None
        best: Path | None = None
        for f in self._root.glob(f"{session_id}_*.json"):
            if best is None or f.stat().st_mtime > best.stat().st_mtime:
                best = f
        if not best or not best.is_file():
            return None
        return ModeSessionReport.model_validate_json(best.read_text(encoding="utf-8"))
