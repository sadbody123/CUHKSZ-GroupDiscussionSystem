"""API models for audio endpoints."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class AudioAssetResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")
    asset_id: str
    session_id: str | None = None
    turn_id: str | None = None
    asset_kind: str = ""
    file_name: str = ""
    mime_type: str = "audio/wav"
    size_bytes: int | None = None
    provider_name: str | None = None
    transcript_text: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class TranscribeAudioResponse(BaseModel):
    transcript: str
    provider_name: str
    language: str | None = None
    confidence: float | None = None
    asset: AudioAssetResponse | None = None


class SubmitUserAudioResponse(BaseModel):
    session_id: str
    turn_count: int
    created_turn: dict[str, Any]
    transcription: dict[str, Any]
    audio_asset: AudioAssetResponse


class SynthesizeTurnAudioResponse(BaseModel):
    asset: AudioAssetResponse
    download_path: str = Field(description="Relative URL to fetch bytes")


class SessionAudioAssetListResponse(BaseModel):
    session_id: str
    assets: list[AudioAssetResponse]
