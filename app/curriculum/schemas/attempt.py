"""Assignment attempt."""

from __future__ import annotations

from pydantic import BaseModel, Field


class AssignmentAttempt(BaseModel):
    attempt_id: str
    assignment_id: str
    assignment_step_id: str
    learner_id: str | None = None
    session_id: str
    topic_id: str | None = None
    created_at: str = ""
    completed_at: str | None = None
    success_checks: list[dict] = Field(default_factory=list)
    outcome_summary: dict = Field(default_factory=dict)
    artifact_refs: dict = Field(default_factory=dict)
    metadata: dict = Field(default_factory=dict)
