"""Exported learner report."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class LearnerReport(BaseModel):
    report_id: str
    learner_id: str
    generated_at: str = ""
    profile_summary: dict[str, Any] = Field(default_factory=dict)
    progress_points: list[dict[str, Any]] = Field(default_factory=list)
    recommendations: list[dict[str, Any]] = Field(default_factory=list)
    learning_plan: dict[str, Any] | None = None
    proxy_limitations: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
