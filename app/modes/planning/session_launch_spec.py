"""Executable spec for launching a session from a learning plan step."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class SessionLaunchSpec(BaseModel):
    topic_id: str
    mode_id: str | None = None
    preset_id: str | None = None
    drill_id: str | None = None
    assessment_template_id: str | None = None
    runtime_profile_id: str | None = None
    audio_enabled: bool = False
    focus_skills: list[str] = Field(default_factory=list)
    linked_pedagogy_item_ids: list[str] = Field(default_factory=list)
    learner_id: str | None = None
    snapshot_id: str
    metadata: dict[str, Any] = Field(default_factory=dict)
