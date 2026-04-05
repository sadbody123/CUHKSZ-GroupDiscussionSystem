"""Audio asset schema."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class AudioAssetRecord(BaseModel):
    asset_id: str
    session_id: str | None = None
    turn_id: str | None = None
    asset_kind: str = ""
    file_path: str = ""
    file_name: str = ""
    mime_type: str = "audio/wav"
    size_bytes: int | None = None
    duration_ms: int | None = None
    provider_name: str | None = None
    transcript_text: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
