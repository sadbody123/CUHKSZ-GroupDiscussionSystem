"""API models for learner endpoints."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class CreateLearnerRequest(BaseModel):
    learner_id: str
    display_name: str | None = None


class LearnerSummaryResponse(BaseModel):
    learner_id: str
    display_name: str | None = None
    total_sessions: int = 0
    updated_at: str = ""


class LearnerProfileResponse(BaseModel):
    learner_id: str
    display_name: str | None = None
    created_at: str = ""
    updated_at: str = ""
    total_sessions: int = 0
    session_ids: list[str] = Field(default_factory=list)
    preferred_mode: str | None = None
    current_runtime_profile_id: str | None = None
    current_focus_skills: list[str] = Field(default_factory=list)
    strong_skills: list[str] = Field(default_factory=list)
    weak_skills: list[str] = Field(default_factory=list)
    aggregate_metrics: dict[str, Any] = Field(default_factory=dict)
    trend_summary: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)
    proxy_notes: list[str] = Field(
        default_factory=lambda: [
            "Skill scores are training heuristics from transcript rules and optional speech proxies.",
            "Speech-related metrics are not official pronunciation grades.",
        ]
    )


class LearnerTimelineResponse(BaseModel):
    learner_id: str
    points: list[dict[str, Any]] = Field(default_factory=list)


class RecommendationItemResponse(BaseModel):
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


class LearningPlanResponse(BaseModel):
    plan_id: str
    learner_id: str
    created_at: str = ""
    horizon_sessions: int = 4
    steps: list[dict[str, Any]] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class LearnerReportResponse(BaseModel):
    report_id: str
    learner_id: str
    generated_at: str = ""
    profile_summary: dict[str, Any] = Field(default_factory=dict)
    progress_points: list[dict[str, Any]] = Field(default_factory=list)
    recommendations: list[dict[str, Any]] = Field(default_factory=dict)
    learning_plan: dict[str, Any] | None = None
    proxy_limitations: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class AttachSessionToLearnerRequest(BaseModel):
    learner_id: str


class AttachSessionToLearnerResponse(BaseModel):
    learner_id: str
    session_id: str
    ingested: bool = False


class RebuildLearnerResponse(BaseModel):
    learner_id: str
    status: str = "ok"
