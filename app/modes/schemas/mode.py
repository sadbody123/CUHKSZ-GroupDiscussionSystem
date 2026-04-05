"""PracticeMode schema."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class PracticeMode(BaseModel):
    mode_id: str
    mode_type: str  # practice | drill | assessment | speech_focus
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
