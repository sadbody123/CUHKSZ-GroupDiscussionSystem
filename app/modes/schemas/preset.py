"""ScenarioPreset schema."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ScenarioPreset(BaseModel):
    preset_id: str
    mode_id: str
    display_name: str
    description: str | None = None
    topic_policy: dict[str, Any] = Field(default_factory=dict)
    role_policy: dict[str, Any] = Field(default_factory=dict)
    runtime_profile_override: str | None = None
    audio_policy: dict[str, Any] = Field(default_factory=dict)
    constraint_overrides: dict[str, Any] = Field(default_factory=dict)
    starter_prompts: list[str] = Field(default_factory=list)
    success_focus: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
