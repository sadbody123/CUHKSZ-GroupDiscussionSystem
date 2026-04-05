"""API models for practice modes."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ModeSummaryResponse(BaseModel):
    mode_id: str
    mode_type: str
    display_name: str
    tags: list[str] = Field(default_factory=list)


class ModeDetailResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")

    mode_id: str
    mode_type: str
    display_name: str
    description: str | None = None
    default_runtime_profile_id: str | None = None
    default_audio_enabled: bool | None = None
    allow_mid_session_coach: bool = True
    auto_generate_feedback: bool = True
    constraint_policy: dict[str, Any] = Field(default_factory=dict)
    timer_policy: dict[str, Any] = Field(default_factory=dict)
    recommended_for_skills: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class PresetSummaryResponse(BaseModel):
    preset_id: str
    mode_id: str
    display_name: str
    tags: list[str] = Field(default_factory=list)


class PresetDetailResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")

    preset_id: str
    mode_id: str
    display_name: str
    description: str | None = None
    topic_policy: dict[str, Any] = Field(default_factory=dict)
    role_policy: dict[str, Any] = Field(default_factory=dict)
    runtime_profile_override: str | None = None
    audio_policy: dict[str, Any] = Field(default_factory=dict)
    constraint_overrides: dict[str, Any] = Field(default_factory=dict)
    starter_prompts: list[str] = Field(default_factory=list)
    success_focus: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class AssessmentTemplateResponse(BaseModel):
    template_id: str
    display_name: str
    description: str | None = None
    simulated_group_size: int = 4
    prep_seconds: int | None = None
    discussion_seconds: int = 0
    metadata: dict[str, Any] = Field(default_factory=dict)
    simulation_note: str = ""


class DrillRecommendationResponse(BaseModel):
    drill_id: str
    title: str
    objective: str = ""
    target_skills: list[str] = Field(default_factory=list)
    reason: str = ""
    suggested_mode_id: str | None = None
    runtime_profile_id: str | None = None
    score: int | None = None


class ModeStatusResponse(BaseModel):
    session_id: str
    mode_id: str | None = None
    preset_id: str | None = None
    drill_id: str | None = None
    assessment_template_id: str | None = None
    mode_state: dict[str, Any] = Field(default_factory=dict)
    timer_state: dict[str, Any] = Field(default_factory=dict)
    simulation_note: str | None = None


class ModeReportResponse(BaseModel):
    report_id: str
    session_id: str
    mode_id: str | None = None
    preset_id: str | None = None
    drill_id: str | None = None
    assessment_template_id: str | None = None
    created_at: str = ""
    phase_progress: dict[str, Any] = Field(default_factory=dict)
    strengths: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    proxy_notes: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
