"""Evidence chunks derived from normalized documents."""

from __future__ import annotations

from pydantic import BaseModel, Field


class EvidenceChunk(BaseModel):
    """A slice of text tied to a document for future retrieval / practice."""

    chunk_id: str
    doc_id: str
    text: str
    source_type: str
    evidence_type: str
    topic_tags: list[str] = Field(default_factory=list)
    citation: str | None = None
    quality_score: float | None = None
    metadata: dict = Field(default_factory=dict)
