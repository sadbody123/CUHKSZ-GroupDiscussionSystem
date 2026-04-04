"""Canonical document shape after adapter + normalization."""

from __future__ import annotations

from pydantic import BaseModel, Field


class NormalizedDocument(BaseModel):
    """Unified downstream document."""

    doc_id: str
    source_table: str
    source_id: str | None = None
    title: str | None = None
    url: str | None = None
    published_at: str | None = None
    language: str | None = None
    clean_text: str
    source_type: str
    raw_record_ref: str | None = None
    metadata: dict = Field(default_factory=dict)
