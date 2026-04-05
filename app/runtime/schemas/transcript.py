"""Single turn in a discussion transcript."""

from __future__ import annotations

from pydantic import BaseModel, Field


class TranscriptTurn(BaseModel):
    turn_id: str
    speaker_role: str
    speaker_name: str | None = None
    text: str
    created_at: str = ""
    input_mode: str = "text"
    audio_asset_id: str | None = None
    transcript_source: str | None = None
    tts_asset_id: str | None = None
    speech_analysis_id: str | None = None
    participant_id: str | None = None
    team_id: str | None = None
    speaker_display_name: str | None = None
    turn_relation_to_user: str | None = None
    turn_role_type: str | None = None
    metadata: dict = Field(default_factory=dict)
