"""Explainable recommendation item."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class RecommendationItem(BaseModel):
    recommendation_id: str
    recommendation_type: str
    title: str
    reason: str
    priority: str | None = None
    linked_topic_ids: list[str] = Field(default_factory=list)
    linked_pedagogy_item_ids: list[str] = Field(default_factory=list)
    suggested_runtime_profile_id: str | None = None
    suggested_mode: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
