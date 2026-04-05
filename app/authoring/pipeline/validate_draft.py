"""Validate draft pipeline."""

from __future__ import annotations

import json
from pathlib import Path

from app.authoring.engines.validator import run_validation
from app.authoring.schemas.draft import AuthoringDraft
from app.authoring.schemas.validation import ValidationReport


def run_validate_draft(draft: AuthoringDraft, report_path: Path) -> ValidationReport:
    rep = run_validation(draft)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(rep.model_dump(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return rep
