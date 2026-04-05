"""TTS request/response."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class SynthesisRequest(BaseModel):
    provider_name: str = "mock_tts"
    text: str
    voice: str | None = None
    role: str | None = None
    session_id: str | None = None
    turn_id: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class SynthesisResponse(BaseModel):
    provider_name: str
    mime_type: str = "audio/wav"
    audio_bytes: bytes = b""
    duration_ms: int | None = None
    raw: dict[str, Any] | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
