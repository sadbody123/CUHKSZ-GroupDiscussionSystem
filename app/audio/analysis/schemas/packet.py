"""Turn-level speech analysis packet."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class SpeechAnalysisPacket(BaseModel):
    analysis_id: str
    session_id: str | None = None
    turn_id: str | None = None
    asset_id: str | None = None
    metrics: dict[str, Any] = Field(default_factory=dict)
    signals: list[dict[str, Any]] = Field(default_factory=list)
    strengths: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    recommended_pedagogy_item_ids: list[str] = Field(default_factory=list)
    proxy_disclaimer: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)
