"""Single turn in a discussion transcript."""

from __future__ import annotations

from pydantic import BaseModel, Field


class TranscriptTurn(BaseModel):
    turn_id: str
    speaker_role: str
    speaker_name: str | None = None
    text: str
    created_at: str = ""
    metadata: dict = Field(default_factory=dict)
