"""Preview sandbox (deterministic, non-destructive)."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from app.application.config import AppConfig
from app.authoring.engines import artifact_resolver
from app.authoring.schemas.draft import AuthoringDraft
from app.authoring.schemas.preview import PreviewResult
from app.curriculum.schemas.pack import CurriculumPack


def run_preview(
    cfg: AppConfig,
    draft: AuthoringDraft,
    *,
    preview_kind: str,
    snapshot_id: str | None,
    provider_name: str | None,
    learner_id: str | None,
) -> PreviewResult:
    now = datetime.now(timezone.utc).isoformat()
    warnings: list[str] = []
    summary: dict[str, Any] = {"preview_kind": preview_kind, "draft_id": draft.draft_id}
    generated_refs: dict[str, Any] = {}
    success = True

    if preview_kind == "artifact_render":
        summary["rendered_keys"] = list(draft.content.keys())[:40]
        generated_refs["structure"] = "ok"

    elif preview_kind == "launch_spec":
        if draft.artifact_type == "curriculum_pack":
            try:
                cp = CurriculumPack.model_validate(draft.content)
                first = sorted(cp.steps, key=lambda s: s.order)[0] if cp.steps else None
                summary["launch"] = {
                    "pack_id": cp.pack_id,
                    "topic_id": first.topic_id if first else None,
                    "mode_id": first.mode_id if first else None,
                    "runtime_profile_id": first.runtime_profile_id if first else None,
                }
            except Exception as e:
                success = False
                warnings.append(f"curriculum pack parse: {e}")

    elif preview_kind == "pack_walkthrough":
        steps = (draft.content or {}).get("steps") or []
        summary["step_count"] = len(steps) if isinstance(steps, list) else 0
        summary["snapshot_id"] = snapshot_id
        generated_refs["sandbox"] = f"preview_{uuid.uuid4().hex[:8]}"

    elif preview_kind == "drill_preview":
        skills = (draft.content or {}).get("target_skills") or []
        summary["targets"] = skills
        summary["learner_id"] = learner_id

    elif preview_kind == "retrieval_preview":
        warnings.append("Retrieval preview is minimal in phase 16; use indexing benchmarks for full checks.")
        summary["hint"] = "Would intersect topic_card keywords with snapshot lexical index (not executed here)."

    elif preview_kind == "feedback_preview":
        warnings.append("Feedback preview uses draft metadata only; does not run full coach pipeline.")
        summary["metadata_keys"] = list((draft.metadata or {}).keys())

    else:
        success = False
        warnings.append(f"unknown preview_kind: {preview_kind}")

    # lineage / base visibility
    if draft.base_artifact_ref_id:
        base = artifact_resolver.load_base_content_for_derivative(cfg, draft.artifact_type, draft.artifact_id)
        summary["has_base_snapshot"] = base is not None

    return PreviewResult(
        preview_result_id=f"prv_{uuid.uuid4().hex[:12]}",
        draft_id=draft.draft_id,
        preview_id=f"pspec_{uuid.uuid4().hex[:8]}",
        preview_kind=preview_kind,
        created_at=now,
        success=success,
        summary=summary,
        warnings=warnings,
        generated_refs=generated_refs,
        metadata={"provider_name": provider_name, "proxy_safe": True},
    )
