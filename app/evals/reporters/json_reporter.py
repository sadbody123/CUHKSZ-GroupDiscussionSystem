"""JSON report."""

from __future__ import annotations

import json
from pathlib import Path

from app.evals.schemas.report import EvalReport


def write(path: Path, report: EvalReport) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report.model_dump(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
