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


class CreateSessionResponse(BaseModel):
    session_id: str
    phase: str
    topic_id: str | None
    provider_name: str
    runtime_profile_id: str = "default"
    created_at: str


class SessionStatusResponse(BaseModel):
    session_id: str
    topic_id: str | None
    phase: str
    runtime_profile_id: str = "default"
    provider_name: str
    model_name: str | None = None
    turn_count: int
    latest_turns: list[dict[str, Any]]
    feedback_ready: bool
    coach_report_present: bool
    coach_text_preview: str | None = None
    can_run_next: bool
    peek_next_role: str | None = None


class SessionListItemResponse(BaseModel):
    session_id: str
    topic_id: str | None
    phase: str
    turn_count: int
    provider_name: str
