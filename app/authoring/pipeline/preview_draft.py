"""Preview draft pipeline."""

from __future__ import annotations

import json
from pathlib import Path

from app.application.config import AppConfig
from app.authoring.engines.preview_runner import run_preview
from app.authoring.schemas.draft import AuthoringDraft
from app.authoring.schemas.preview import PreviewResult


def run_preview_draft(
    cfg: AppConfig,
    draft: AuthoringDraft,
    *,
    preview_kind: str,
    snapshot_id: str | None,
    provider_name: str | None,
    learner_id: str | None,
    result_path: Path,
) -> PreviewResult:
    res = run_preview(
        cfg,
        draft,
        preview_kind=preview_kind,
        snapshot_id=snapshot_id,
        provider_name=provider_name,
        learner_id=learner_id,
    )
    result_path.parent.mkdir(parents=True, exist_ok=True)
    result_path.write_text(json.dumps(res.model_dump(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return res
