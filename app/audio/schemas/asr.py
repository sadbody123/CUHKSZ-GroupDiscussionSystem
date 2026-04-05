"""ASR request/response."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class TranscriptionRequest(BaseModel):
    provider_name: str = "mock_asr"
    file_path: str | None = None
    audio_bytes: bytes | None = None
    mime_type: str | None = None
    language_hint: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class TranscriptionResponse(BaseModel):
    provider_name: str
    text: str
    language: str | None = None
    confidence: float | None = None
    raw: dict[str, Any] | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
