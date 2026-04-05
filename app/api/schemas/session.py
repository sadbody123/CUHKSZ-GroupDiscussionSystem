"""Session API models."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class CreateSessionRequest(BaseModel):
    snapshot_id: str
    topic_id: str
    user_stance: str | None = None
    provider_name: str | None = None
    model_name: str | None = None
    max_discussion_turns: int | None = Field(default=None, ge=1, le=500)
    runtime_profile_id: str | None = None
    learner_id: str | None = None
    mode_id: str | None = None
    preset_id: str | None = None
    drill_id: str | None = None
    assessment_template_id: str | None = None
    roster_template_id: str | None = None
    user_participant_id: str | None = None
    participant_name_overrides: dict[str, str] | None = None


class CreateSessionResponse(BaseModel):
    session_id: str
    phase: str
    topic_id: str | None
    provider_name: str
    runtime_profile_id: str = "default"
    created_at: str
    learner_id: str | None = None
    mode_id: str | None = None
    preset_id: str | None = None
    drill_id: str | None = None
    assessment_template_id: str | None = None
    roster_template_id: str | None = None
    user_participant_id: str | None = None


class SessionStatusResponse(BaseModel):
    session_id: str
    topic_id: str | None
    learner_id: str | None = None
    mode_id: str | None = None
    preset_id: str | None = None
    drill_id: str | None = None
    assessment_template_id: str | None = None
    mode_report_id: str | None = None
    mode_state: dict[str, Any] = Field(default_factory=dict)
    timer_state: dict[str, Any] = Field(default_factory=dict)
    simulation_note: str | None = None
    phase: str
    runtime_profile_id: str = "default"
    retrieval_mode: str = "rule"
    has_indexes: bool = False
    provider_name: str
    model_name: str | None = None
    turn_count: int
    latest_turns: list[dict[str, Any]]
    feedback_ready: bool
    coach_report_present: bool
    coach_text_preview: str | None = None
    can_run_next: bool
    peek_next_role: str | None = None
    audio_enabled: bool = False
    asr_provider_name: str | None = None
    tts_provider_name: str | None = None
    audio_asset_count: int = 0
    speech_report_id: str | None = None
    speech_analysis_enabled: bool = False
    roster_template_id: str | None = None
    user_participant_id: str | None = None
    participants: list[dict[str, Any]] = Field(default_factory=list)
    teams: list[dict[str, Any]] = Field(default_factory=list)
    group_balance_report_id: str | None = None
    next_candidate_participant_ids: list[str] = Field(default_factory=list)
    curriculum_pack_id: str | None = None
    assignment_id: str | None = None
    assignment_step_id: str | None = None


class SessionListItemResponse(BaseModel):
    session_id: str
    topic_id: str | None
    phase: str
    turn_count: int
    provider_name: str
    learner_id: str | None = None
