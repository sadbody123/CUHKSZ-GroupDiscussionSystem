"""CLI/API entry: run consistency audit and optional persist."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.application.config import AppConfig, get_app_config
from app.stability.engines.consistency_auditor import run_consistency_audit


def run_consistency_audit_pipeline(
    profile_id: str,
    *,
    cfg: AppConfig | None = None,
    output_json: Path | None = None,
) -> dict[str, Any]:
    cfg = cfg or get_app_config()
    findings, summary = run_consistency_audit(profile_id, cfg=cfg)
    row = {
        "profile_id": profile_id,
        "summary": summary,
        "findings": [f.model_dump() for f in findings],
    }
    if output_json:
        output_json.parent.mkdir(parents=True, exist_ok=True)
        output_json.write_text(json.dumps(row, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return row
