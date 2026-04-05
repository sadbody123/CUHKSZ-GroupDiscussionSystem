"""Cross-interface consistency summary (release profile vs gates)."""

from __future__ import annotations

from typing import Any

from app.release.engines.feature_gate import load_profile_or_default
from app.release.pipeline.build_capability_matrix import build_capability_matrix_json


def build_interface_consistency_summary(profile_id: str) -> dict[str, Any]:
    prof = load_profile_or_default(profile_id)
    matrix = build_capability_matrix_json(profile_id)
    enabled = {r["capability_id"] for r in matrix.get("capabilities", []) if r.get("enabled")}
    hidden_panels = [k for k, v in (prof.ui_visibility_policy or {}).items() if v is False]
    hidden_api = [k for k, v in (prof.api_visibility_policy or {}).items() if v is False]
    mismatches: list[str] = []
    if "authoring_studio" in prof.experimental_capabilities and prof.ui_visibility_policy.get("authoring_studio") is False:
        mismatches.append("authoring_studio: experimental but UI hidden (expected for demo profiles)")
    return {
        "profile_id": prof.profile_id,
        "enabled_capability_count": len(enabled),
        "experimental_capabilities": list(prof.experimental_capabilities or []),
        "ui_hidden_keys": hidden_panels,
        "api_hidden_keys": hidden_api,
        "notes": mismatches,
        "consistent": len(mismatches) == 0,
    }
