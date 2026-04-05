"""Index manifest written under snapshot ``indexes/``."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class IndexManifest(BaseModel):
    index_id: str
    snapshot_id: str
    created_at: str
    schema_version: str = "1.0"
    embedder_name: str = "hash"
    embedder_model: str | None = None
    dimension: int | None = None
    stores: list[str] = Field(default_factory=list)
    available_modes: list[str] = Field(default_factory=list)
    item_counts: dict[str, int] = Field(default_factory=dict)
    files: list[dict[str, Any]] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
