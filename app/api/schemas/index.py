"""Index status API models."""

from __future__ import annotations

from pydantic import BaseModel, Field


class IndexStatusResponse(BaseModel):
    snapshot_id: str
    has_indexes: bool
    available_modes: list[str] = Field(default_factory=list)
    stores: list[str] = Field(default_factory=list)
    embedder_name: str | None = None
    dimension: int | None = None
    item_counts: dict[str, int] = Field(default_factory=dict)
