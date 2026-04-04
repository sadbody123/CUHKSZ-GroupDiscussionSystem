"""Structured filters for retrieval (rule-based)."""

from __future__ import annotations

from pydantic import BaseModel, Field


class EvidenceQuery(BaseModel):
    topic_tag: str | None = None
    topic_id: str | None = None
    source_type: str | None = None
    evidence_type: str | None = None
    min_quality: float | None = None
    min_credibility: float | None = None
    keyword: str | None = None
    top_k: int = 8
    stance_hint: str | None = None


class PedagogyQuery(BaseModel):
    item_type: str | None = None
    category: str | None = None
    tags: list[str] | None = None
    language: str | None = None
    session_phase: str | None = None
    top_k: int = 8
