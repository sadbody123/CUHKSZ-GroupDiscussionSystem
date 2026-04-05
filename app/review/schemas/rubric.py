"""Manual rubric scoring."""

from __future__ import annotations

from pydantic import BaseModel, Field


class RubricDimension(BaseModel):
    """Workspace-visible rubric dimension (from pedagogy or fallback)."""

    dimension_id: str
    dimension_name: str
    max_score: float | None = None
    description: str | None = None
    source: str = "fallback"  # pedagogy | fallback
    metadata: dict = Field(default_factory=dict)


class ManualRubricScore(BaseModel):
    score_id: str
    dimension_id: str
    dimension_name: str
    score: float | None = None
    max_score: float | None = None
    confidence: float | None = None
    note: str | None = None
    metadata: dict = Field(default_factory=dict)
