"""Human-readable capability matrix."""

from __future__ import annotations

from app.release.engines.feature_gate import is_capability_enabled, load_profile_or_default
from app.release.pipeline.build_capability_matrix import build_capability_matrix_json


def build_capability_matrix_markdown(profile_id: str) -> str:
    data = build_capability_matrix_json(profile_id)
    lines = [f"# Capability matrix — {profile_id}", ""]
    for row in data.get("capabilities", []):
        lines.append(
            f"| {row.get('capability_id')} | {row.get('stability')} | {row.get('enabled')} | {row.get('area')} |"
        )
    lines.insert(2, "| id | stability | enabled | area |")
    lines.insert(3, "| --- | --- | --- | --- |")
    return "\n".join(lines)
