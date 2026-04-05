"""Export calibration / review summary to JSON or Markdown."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def export_calibration_json(report: dict[str, Any], path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def export_calibration_markdown(report: dict[str, Any], path: Path) -> Path:
    lines = [
        f"# Calibration report {report.get('report_id', '')}",
        "",
        f"- overall_agreement: {report.get('overall_agreement')}",
        "",
        "## Key mismatches",
    ]
    for m in report.get("key_mismatches") or []:
        lines.append(f"- {m}")
    lines.append("")
    lines.append("## Suggested actions")
    for m in report.get("suggested_actions") or []:
        lines.append(f"- {m}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path
