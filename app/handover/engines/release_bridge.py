"""Aggregate release + stability signals for handover (no duplicate business logic)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from app.application.config import AppConfig
from app.application.release_service import ReleaseService
from app.application.stability_service import StabilityService
from app.ops.settings import UnifiedSettings


def list_snapshot_ids(cfg: AppConfig, s: UnifiedSettings) -> list[str]:
    root = Path(cfg.snapshot_root)
    out: list[str] = []
    if not root.is_dir():
        return out
    for child in sorted(root.iterdir()):
        if not child.is_dir():
            continue
        if (child / "manifest.json").is_file():
            out.append(child.name)
    return out


def gather_handover_context(
    profile_id: str,
    *,
    cfg: AppConfig,
    release: ReleaseService,
    stability: StabilityService,
    ops: UnifiedSettings,
) -> dict[str, Any]:
    readiness = release.run_readiness_audit(profile_id).model_dump()
    stability_rep = stability.get_stability_report(profile_id, include_e2e=False)
    rc_rep = stability.build_rc_report(profile_id)
    cap = release.get_capability_matrix(profile_id)
    issues = stability.list_known_issues()
    snaps = list_snapshot_ids(cfg, ops)
    prof = release.get_release_profile(profile_id)
    demo_ids = list(prof.get("demo_scenario_ids") or [])
    return {
        "profile_id": profile_id,
        "readiness": readiness,
        "stability_report": stability_rep,
        "rc_report": rc_rep,
        "capability_matrix": cap,
        "known_issues": issues,
        "snapshot_ids": snaps,
        "demo_scenario_ids": demo_ids,
    }


def logical_ref_key(kind: str, name: str) -> str:
    return f"{kind}:{name}"
