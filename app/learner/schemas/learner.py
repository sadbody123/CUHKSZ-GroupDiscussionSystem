"""Learner profile aggregate."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class LearnerProfile(BaseModel):
    learner_id: str
    display_name: str | None = None
    created_at: str = ""
    updated_at: str = ""
    total_sessions: int = 0
    session_ids: list[str] = Field(default_factory=list)
    preferred_mode: str | None = None  # text | audio | mixed
    current_runtime_profile_id: str | None = None
    current_focus_skills: list[str] = Field(default_factory=list)
    strong_skills: list[str] = Field(default_factory=list)
    weak_skills: list[str] = Field(default_factory=list)
    aggregate_metrics: dict[str, Any] = Field(default_factory=dict)
    trend_summary: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)
