"""DTOs for runtime V2 review console APIs."""

from __future__ import annotations

from pydantic import BaseModel, Field


class RuntimeReviewSummaryResponse(BaseModel):
    review_id: str
    session_id: str
    run_id: str
    topic_id: str | None = None
    status: str
    interrupt_reason: str | None = None
    quality_flags: list[str] = Field(default_factory=list)
    version: int
    allowed_actions: list[str] = Field(default_factory=list)
    updated_at: str


class RuntimeReviewDetailResponse(RuntimeReviewSummaryResponse):
    checkpoint_id: str | None = None
    reason: str | None = None
    draft_reply_text: str | None = None
    draft_reply_summary: str | None = None
    review_decision_payload: dict = Field(default_factory=dict)
    notes: list[str] = Field(default_factory=list)
    resolved_by: str | None = None
    updated_by: str | None = None
    metadata: dict = Field(default_factory=dict)
    created_at: str


class ApproveRuntimeReviewRequest(BaseModel):
    action: str = "approve"  # approve or reject
    expected_version: int | None = None
    updated_by: str | None = None
    payload: dict = Field(default_factory=dict)


class RejectRuntimeReviewRequest(BaseModel):
    reason: str | None = None
    expected_version: int | None = None
    updated_by: str | None = None


class ResumeRuntimeReviewRequest(BaseModel):
    additional_steps: int = 1


class ApplyEditedDraftRequest(BaseModel):
    edited_text: str
    expected_version: int | None = None
    updated_by: str | None = None
    note: str | None = None
    resume_after_apply: bool = False
    additional_steps: int = 1


class RuntimeReviewActionResponse(BaseModel):
    review: RuntimeReviewDetailResponse
    result: dict = Field(default_factory=dict)


class RuntimeReviewMetricsResponse(BaseModel):
    created_review_count: int
    pending_review_count: int
    resolved_review_count: int
    interrupt_rate: float
    repair_rate: float
    manual_override_count: int
