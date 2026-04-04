"""Enriched evidence record for training systems (extends chunk-level data)."""

from __future__ import annotations

from pydantic import BaseModel, Field


class EvidenceIndexItem(BaseModel):
    """
    Training-facing evidence row: chunk-level text plus scoring and stance hints.

    Distinct from EvidenceChunk: adds stance_hint, credibility_score, stable title linkage.
    """

    evidence_id: str
    chunk_id: str
    doc_id: str
    text: str
    title: str | None = None
    source_type: str
    evidence_type: str
    topic_tags: list[str] = Field(default_factory=list)
    stance_hint: str | None = None
    citation: str | None = None
    quality_score: float | None = None
    credibility_score: float | None = None
    metadata: dict = Field(default_factory=dict)
