"""Coach natural-language report."""

from __future__ import annotations

from pydantic import BaseModel, Field


class CoachReport(BaseModel):
    session_id: str
    topic_id: str | None = None
    text: str
    strengths: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    suggested_next_actions: list[str] = Field(default_factory=list)
    feedback_packet: dict = Field(default_factory=dict)
    metadata: dict = Field(default_factory=dict)
