"""Rule-based feedback aggregate (no LLM)."""

from __future__ import annotations

from pydantic import BaseModel, Field


class FeedbackPacket(BaseModel):
    session_id: str
    topic_id: str | None = None
    metrics: dict = Field(default_factory=dict)
    detected_signals: list[dict] = Field(default_factory=list)
    strengths: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    recommended_pedagogy_item_ids: list[str] = Field(default_factory=list)
    speech_session_report: dict | None = None
    speech_proxy_disclaimer: str | None = None
    metadata: dict = Field(default_factory=dict)
