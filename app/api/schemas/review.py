"""API models for review workspace."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class CreateReviewerRequest(BaseModel):
    reviewer_id: str
    display_name: str
    role_title: str | None = None


class ReviewerSummaryResponse(BaseModel):
    reviewer_id: str
    display_name: str
    role_title: str | None = None
    created_at: str


class ReviewerDetailResponse(ReviewerSummaryResponse):
    preferred_rubric_id: str | None = None
    notes: list[str] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)


class ReviewPackSummaryResponse(BaseModel):
    review_pack_id: str
    session_id: str
    status: str
    created_at: str
    topic_id: str | None = None
    mode_id: str | None = None


class ReviewPackDetailResponse(BaseModel):
    review_pack_id: str
    session_id: str
    learner_id: str | None = None
    topic_id: str | None = None
    mode_id: str | None = None
    roster_template_id: str | None = None
    created_at: str
    status: str
    included_artifacts: dict = Field(default_factory=dict)
    ai_summary: dict = Field(default_factory=dict)
    transcript_ref: str | None = None
    proxy_limitations: list[str] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)
    proxy_note: str = Field(
        default="AI and proxy metrics are for training/calibration only; not official grades.",
    )


class SubmitReviewRequest(BaseModel):
    reviewer_id: str
    rubric_scores: list[dict[str, Any]] = Field(default_factory=list)
    annotations: list[dict[str, Any]] = Field(default_factory=list)
    override_decisions: list[dict[str, Any]] = Field(default_factory=list)
    overall_judgment: str | None = None
    summary_notes: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class SubmitReviewResponse(BaseModel):
    review_id: str
    review_pack_id: str
    reviewer_id: str
    created_at: str


class SessionReviewSummaryResponse(BaseModel):
    session_id: str
    review_count: int
    pack_count: int
    latest_calibration: dict | None = None


class CalibrationReportResponse(BaseModel):
    report_id: str
    review_pack_id: str
    session_id: str
    review_id: str | None = None
    created_at: str
    overall_agreement: str | None = None
    results: list[dict] = Field(default_factory=list)
    key_mismatches: list[str] = Field(default_factory=list)
    suggested_actions: list[str] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)
    proxy_note: str = Field(
        default="Calibration compares AI vs human for training only; not an official arbitration.",
    )


class ReviewedOutputResponse(BaseModel):
    review_pack_id: str
    review_id: str
    reviewer_id: str
    created_at: str
    proxy_note: str | None = None
    payload: dict = Field(default_factory=dict)
