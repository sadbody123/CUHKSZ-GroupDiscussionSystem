"""Assignment report."""

from __future__ import annotations

from pydantic import BaseModel, Field


class AssignmentReport(BaseModel):
    report_id: str
    assignment_id: str
    generated_at: str = ""
    pack_summary: dict = Field(default_factory=dict)
    learner_summaries: list[dict] = Field(default_factory=list)
    step_summaries: list[dict] = Field(default_factory=list)
    completion_summary: dict = Field(default_factory=dict)
    recommended_actions: list[str] = Field(default_factory=list)
    proxy_notes: list[str] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)
