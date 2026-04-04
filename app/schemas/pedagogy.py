"""Pedagogy knowledge base items (rules, rubrics, language bank, coaching)."""

from __future__ import annotations

from pydantic import BaseModel, Field


class PedagogyItem(BaseModel):
    """Structured teaching / coaching content for offline training."""

    item_id: str
    item_type: str
    category: str | None = None
    subcategory: str | None = None
    content: str
    language: str | None = None
    source_ref: str | None = None
    tags: list[str] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)
