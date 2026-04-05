"""Publish drafts to custom artifact locations (never overwrite built-ins)."""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from app.application.config import AppConfig
from app.authoring.constants import AT_CURRICULUM_PACK, AT_RUNTIME_PROFILE
from app.authoring.schemas.draft import AuthoringDraft
from app.authoring.schemas.publication import PublicationRecord
from app.curriculum.loaders.yaml_loader import list_builtin_pack_ids
from app.curriculum.schemas.pack import CurriculumPack
from app.curriculum.store.pack_store import PackStore


def _builtin_curriculum_ids() -> set[str]:
    return set(list_builtin_pack_ids())


def publish_draft(
    cfg: AppConfig,
    draft: AuthoringDraft,
    *,
    published_version: str,
    published_by: str | None,
    validation_report_id: str | None,
    preview_result_ids: list[str],
) -> PublicationRecord:
    now = datetime.now(timezone.utc).isoformat()
    pub_id = f"pub_{uuid.uuid4().hex[:12]}"

    if draft.artifact_type == AT_CURRICULUM_PACK:
        pack = CurriculumPack.model_validate(draft.content)
        if pack.pack_id in _builtin_curriculum_ids():
            raise ValueError(
                f"refusing to publish pack_id {pack.pack_id}: matches built-in id; use a new pack_id for custom publications"
            )
        store = PackStore(cfg.curriculum_pack_builtin_dir, cfg.curriculum_custom_pack_dir)
        out_path = store.save_custom_pack(pack)
        rel = str(out_path.relative_to(cfg.project_root)) if out_path.is_relative_to(cfg.project_root) else str(out_path)

    elif draft.artifact_type == AT_RUNTIME_PROFILE:
        prof_dir = cfg.authoring_published_runtime_profile_dir
        prof_dir.mkdir(parents=True, exist_ok=True)
        pid = str(draft.content.get("profile_id") or draft.artifact_id)
        if pid in _builtin_runtime_ids():
            raise ValueError(f"refusing to publish profile_id {pid}: conflicts with built-in profile stem")
        out_path = prof_dir / f"{pid}.yaml"
        out_path.write_text(yaml.safe_dump(draft.content, allow_unicode=True, sort_keys=False), encoding="utf-8")
        rel = str(out_path.relative_to(cfg.project_root)) if out_path.is_relative_to(cfg.project_root) else str(out_path)

    else:
        sub = {
            "topic_card": "topic_cards",
            "pedagogy_item": "pedagogy_items",
            "drill_spec": "drills",
            "scenario_preset": "presets",
            "assessment_template": "assessment_templates",
            "roster_template": "roster_templates",
        }.get(draft.artifact_type, "misc")
        base = cfg.authoring_published_misc_dir / sub
        base.mkdir(parents=True, exist_ok=True)
        aid = draft.content.get("artifact_id") or draft.content.get("pack_id") or draft.artifact_id
        out_path = base / f"{aid}.json"
        out_path.write_text(json.dumps(draft.content, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        rel = str(out_path.relative_to(cfg.project_root)) if out_path.is_relative_to(cfg.project_root) else str(out_path)

    return PublicationRecord(
        publication_id=pub_id,
        draft_id=draft.draft_id,
        artifact_type=draft.artifact_type,
        artifact_id=str(draft.content.get("pack_id") or draft.content.get("profile_id") or draft.content.get("topic_id") or draft.artifact_id),
        published_version=published_version,
        published_at=now,
        published_by=published_by,
        output_ref=rel,
        derivative_of=draft.derivative_of,
        validation_report_id=validation_report_id,
        preview_result_ids=list(preview_result_ids),
        change_summary=list(draft.change_summary),
        metadata={"lineage": draft.metadata.get("lineage", {})},
    )


def _builtin_runtime_ids() -> set[str]:
    from app.runtime.profile_loader import list_profile_ids

    return set(list_profile_ids())
