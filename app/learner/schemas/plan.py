"""Learning plan schemas."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class LearningPlanStep(BaseModel):
    step_id: str
    order: int
    title: str
    objective: str = ""
    topic_id: str | None = None
    runtime_profile_id: str | None = None
    mode: str | None = None
    focus_skills: list[str] = Field(default_factory=list)
    linked_pedagogy_item_ids: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class LearningPlan(BaseModel):
    plan_id: str
    learner_id: str
    created_at: str = ""
    horizon_sessions: int = 4
    steps: list[dict[str, Any]] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
