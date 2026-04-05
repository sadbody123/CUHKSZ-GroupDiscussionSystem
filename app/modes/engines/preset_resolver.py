"""Merge mode defaults with preset overrides."""

from __future__ import annotations

from typing import Any

from app.modes.schemas.mode import PracticeMode
from app.modes.schemas.preset import ScenarioPreset


def merged_constraint_policy(mode: PracticeMode, preset: ScenarioPreset | None) -> dict[str, Any]:
    base = dict(mode.constraint_policy or {})
    if not preset:
        return base
    ov = dict(preset.constraint_overrides or {})
    return {**base, **ov}


def effective_runtime_profile(mode: PracticeMode, preset: ScenarioPreset | None, current: str) -> str:
    if preset and preset.runtime_profile_override:
        return preset.runtime_profile_override
    # Caller explicitly chose a non-default profile — do not replace with mode default.
    if current and current != "default":
        return current
    if mode.default_runtime_profile_id:
        return mode.default_runtime_profile_id
    return current or "default"
