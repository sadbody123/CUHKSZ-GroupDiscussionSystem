"""Single-session progress snapshot."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ProgressPoint(BaseModel):
    point_id: str
    learner_id: str
    session_id: str
    created_at: str = ""
    metrics: dict[str, Any] = Field(default_factory=dict)
    skill_scores: dict[str, float | None] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)
