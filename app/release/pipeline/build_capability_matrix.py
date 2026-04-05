"""Build capability matrix JSON."""

from __future__ import annotations

from typing import Any

from app.release.engines.capability_registry import all_capabilities
from app.release.engines.feature_gate import is_capability_enabled, load_profile_or_default


def build_capability_matrix_json(profile_id: str) -> dict[str, Any]:
    profile = load_profile_or_default(profile_id)
    rows = []
    for c in all_capabilities():
        rows.append(
            {
                "capability_id": c.capability_id,
                "display_name": c.display_name,
                "area": c.area,
                "stability": c.stability,
                "enabled": is_capability_enabled(profile, c.capability_id),
                "experimental": c.capability_id in profile.experimental_capabilities,
            }
        )
    return {"profile_id": profile_id, "capabilities": rows}
