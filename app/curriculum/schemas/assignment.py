"""Assignment schemas."""

from __future__ import annotations

from pydantic import BaseModel, Field


class AssignmentStepRef(BaseModel):
    assignment_step_id: str
    pack_step_id: str
    learner_id: str | None = None
    required: bool = True
    status: str = "pending"
    attempt_ids: list[str] = Field(default_factory=list)
    latest_session_id: str | None = None
    completion_summary: dict = Field(default_factory=dict)
    metadata: dict = Field(default_factory=dict)


class AssignmentSpec(BaseModel):
    assignment_id: str
    pack_id: str
    learner_ids: list[str] = Field(default_factory=list)
    created_at: str = ""
    created_by: str | None = None
    title: str = ""
    description: str | None = None
    due_at: str | None = None
    status: str = "draft"
    total_steps: int = 0
    completion_policy: dict = Field(default_factory=dict)
    step_refs: list[AssignmentStepRef] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)
