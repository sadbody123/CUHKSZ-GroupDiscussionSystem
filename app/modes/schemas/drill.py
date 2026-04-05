"""DrillSpec schema."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class DrillSpec(BaseModel):
    drill_id: str
    drill_type: str
    title: str
    objective: str = ""
    target_skills: list[str] = Field(default_factory=list)
    suggested_mode_id: str | None = None
    runtime_profile_id: str | None = None
    recommended_duration_minutes: int | None = None
    prompt_instructions: list[str] = Field(default_factory=list)
    success_criteria: list[str] = Field(default_factory=list)
    remediation_hints: list[str] = Field(default_factory=list)
    linked_topic_ids: list[str] = Field(default_factory=list)
    linked_pedagogy_item_ids: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
