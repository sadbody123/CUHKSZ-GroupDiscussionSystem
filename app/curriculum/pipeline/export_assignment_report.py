"""Export report JSON/Markdown."""

from __future__ import annotations

import json
from pathlib import Path

from app.curriculum.schemas.report import AssignmentReport


def export_report_json(report: AssignmentReport, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report.model_dump(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def export_report_markdown(report: AssignmentReport, path: Path) -> Path:
    lines = [
        f"# Assignment report {report.report_id}",
        "",
        f"- assignment_id: {report.assignment_id}",
        "",
        "## Recommended actions",
    ]
    for a in report.recommended_actions:
        lines.append(f"- {a}")
    lines.append("")
    lines.append("## Proxy notes")
    for n in report.proxy_notes:
        lines.append(f"- {n}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path
