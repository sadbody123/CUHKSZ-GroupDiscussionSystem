"""Topic API models."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class TopicSummaryResponse(BaseModel):
    topic_id: str
    topic: str = ""
    summary: str | None = None
    tags: list[str] = Field(default_factory=list)


class TopicDetailResponse(BaseModel):
    card: dict[str, Any]
