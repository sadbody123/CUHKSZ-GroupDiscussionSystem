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
    selected_role_policy: str | None = None
    turns: list[TranscriptTurn] = Field(default_factory=list)
    coach_report: dict | None = None
    metadata: dict = Field(default_factory=dict)
