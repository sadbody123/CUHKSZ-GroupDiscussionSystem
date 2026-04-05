"""Session aggregate context."""

from __future__ import annotations

from pydantic import BaseModel, Field

from app.runtime.schemas.transcript import TranscriptTurn


class SessionContext(BaseModel):
    """Persisted discussion session (file-backed)."""

    session_id: str
    topic_id: str | None = None
    user_stance: str | None = None
    phase: str = "prepare"
    max_discussion_turns: int | None = None
    provider_name: str = "mock"
    model_name: str | None = None
    snapshot_dir: str | None = None
    runtime_profile_id: str = "default"
    learner_id: str | None = None
    mode_id: str | None = None
    preset_id: str | None = None
    drill_id: str | None = None
    assessment_template_id: str | None = None
    mode_state: dict = Field(default_factory=dict)
    timer_state: dict = Field(default_factory=dict)
    mode_report_id: str | None = None
    roster_template_id: str | None = None
    participants: list[dict] = Field(default_factory=list)
    teams: list[dict] = Field(default_factory=list)
    user_participant_id: str | None = None
    seat_policies: dict = Field(default_factory=dict)
    participant_memory_state: dict = Field(default_factory=dict)
    group_balance_report_id: str | None = None
    next_candidate_participant_ids: list[str] | None = None
    selected_role_policy: str | None = None
    turns: list[TranscriptTurn] = Field(default_factory=list)
    coach_report: dict | None = None
    audio_enabled: bool = False
    asr_provider_name: str | None = None
    tts_provider_name: str | None = None
    auto_tts_for_ai: bool = False
    audio_asset_ids: list[str] = Field(default_factory=list)
    speech_report_id: str | None = None
    speech_analysis_enabled: bool | None = None
    curriculum_pack_id: str | None = None
    assignment_id: str | None = None
    assignment_step_id: str | None = None
    metadata: dict = Field(default_factory=dict)
