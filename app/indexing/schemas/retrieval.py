"""Retrieval query / hit / result schemas."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class SearchQuery(BaseModel):
    query_text: str | None = None
    topic_id: str | None = None
    topic_tags: list[str] = Field(default_factory=list)
    role: str | None = None
    phase: str | None = None
    top_k: int = 5
    filters: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)


class RetrievalHit(BaseModel):
    item_id: str
    store: str
    score: float
    mode: str
    text: str
    title: str | None = None
    source_type: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class RetrievalResult(BaseModel):
    query: dict[str, Any]
    hits: list[RetrievalHit]
    mode: str
    metadata: dict[str, Any] = Field(default_factory=dict)
