"""Internal DTOs for application services (optional thin wrappers)."""

from __future__ import annotations

from pydantic import BaseModel


class SnapshotListItemDTO(BaseModel):
    snapshot_id: str
    schema_version: str
    created_at: str
    topic_card_count: int
    evidence_index_count: int
    pedagogy_item_count: int
    available: bool = True


class SessionCreatedDTO(BaseModel):
    session_id: str
    phase: str
    topic_id: str | None
    provider_name: str
    created_at: str
