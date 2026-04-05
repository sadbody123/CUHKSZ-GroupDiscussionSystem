"""Review annotations."""

from __future__ import annotations

from pydantic import BaseModel, Field


class ReviewAnnotation(BaseModel):
    annotation_id: str
    target_type: str
    target_id: str | None = None
    annotation_type: str
    content: str
    severity: str | None = None
    linked_turn_ids: list[str] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)
