"""Delivery summary."""

from __future__ import annotations

from pydantic import BaseModel, Field


class DeliverySummary(BaseModel):
    delivery_id: str
    assignment_id: str
    learner_id: str | None = None
    completed_steps: int = 0
    total_steps: int = 0
    completion_rate: float = 0.0
    last_activity_at: str | None = None
    weak_skill_focus: list[str] = Field(default_factory=list)
    recommended_next_step_ids: list[str] = Field(default_factory=list)
    blocked_reasons: list[str] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)
