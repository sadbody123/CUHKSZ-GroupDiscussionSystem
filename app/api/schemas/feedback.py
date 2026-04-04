"""Feedback API models."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class FeedbackResponse(BaseModel):
    session_id: str
    topic_id: str | None
    coach_text: str
    strengths: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    suggested_next_actions: list[str] = Field(default_factory=list)
    feedback_packet: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)
