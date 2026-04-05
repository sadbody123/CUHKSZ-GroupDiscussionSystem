"""Speech analysis API models."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class SpeechAnalysisResponse(BaseModel):
    analysis: dict[str, Any]
    proxy_note: str = Field(default="Heuristic proxy metrics only.")


class SessionSpeechReportResponse(BaseModel):
    report: dict[str, Any] | None = None
    proxy_note: str = Field(default="Heuristic proxy metrics only.")
