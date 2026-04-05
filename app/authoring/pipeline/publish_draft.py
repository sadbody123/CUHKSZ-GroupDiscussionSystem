"""Publish draft pipeline."""

from __future__ import annotations

import json
from pathlib import Path

from app.application.config import AppConfig
from app.authoring.engines.publisher import publish_draft as engine_publish
from app.authoring.schemas.draft import AuthoringDraft
from app.authoring.schemas.publication import PublicationRecord


def run_publish_draft(
    cfg: AppConfig,
    draft: AuthoringDraft,
    *,
    published_version: str,
    published_by: str | None,
    validation_report_id: str | None,
    preview_result_ids: list[str],
    record_path: Path,
) -> PublicationRecord:
    rec = engine_publish(
        cfg,
        draft,
        published_version=published_version,
        published_by=published_by,
        validation_report_id=validation_report_id,
        preview_result_ids=preview_result_ids,
    )
    record_path.parent.mkdir(parents=True, exist_ok=True)
    record_path.write_text(json.dumps(rec.model_dump(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return rec
