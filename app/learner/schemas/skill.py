"""Per-skill longitudinal scores."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class SkillScore(BaseModel):
    skill_id: str
    skill_name: str = ""
    current_score: float | None = None
    recent_score: float | None = None
    baseline_score: float | None = None
    trend: str | None = None  # improving | stable | declining | unknown
    evidence_count: int = 0
    proxy_disclaimer: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
