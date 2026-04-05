"""API models for curriculum / assignments."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class CurriculumPackSummaryResponse(BaseModel):
    pack_id: str
    display_name: str
    version: str | None = None
    target_skills: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)


class CurriculumPackDetailResponse(BaseModel):
    pack_id: str
    display_name: str
    description: str | None = None
    author_id: str | None = None
    version: str | None = None
    target_skills: list[str] = Field(default_factory=list)
    steps: list[dict[str, Any]] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)
    delivery_note: str = Field(
        default="Curriculum packs are training-delivery scaffolds; not an official LMS course outline.",
    )


class CreateAssignmentRequest(BaseModel):
    pack_id: str
    learner_ids: list[str]
    created_by: str | None = None
    title: str
    description: str | None = None
    due_at: str | None = None


class AssignmentSummaryResponse(BaseModel):
    assignment_id: str
    title: str
    pack_id: str
    status: str
    learner_ids: list[str] = Field(default_factory=list)
    created_at: str = ""


class AssignmentDetailResponse(BaseModel):
    assignment_id: str
    pack_id: str
    learner_ids: list[str]
    title: str
    description: str | None = None
    status: str
    total_steps: int
    step_refs: list[dict[str, Any]] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)


class AssignmentProgressResponse(BaseModel):
    assignment: dict[str, Any]
    delivery: dict[str, Any]


class LaunchAssignmentStepRequest(BaseModel):
    snapshot_id: str
    provider_name: str = "mock"
    learner_id: str | None = None


class LaunchAssignmentStepResponse(BaseModel):
    session_id: str
    assignment_id: str
    pack_step_id: str


class AttachSessionAttemptRequest(BaseModel):
    session_id: str


class AttachSessionAttemptResponse(BaseModel):
    attempt_id: str
    step_status: str
    report_id: str | None = None


class AssignmentReportResponse(BaseModel):
    report_id: str
    assignment_id: str
    generated_at: str
    pack_summary: dict = Field(default_factory=dict)
    step_summaries: list[dict] = Field(default_factory=list)
    completion_summary: dict = Field(default_factory=dict)
    recommended_actions: list[str] = Field(default_factory=list)
    proxy_notes: list[str] = Field(default_factory=list)


class CurriculumPackFromPlanRequest(BaseModel):
    horizon: int = 4
    output_pack_id: str
    display_name: str | None = None
