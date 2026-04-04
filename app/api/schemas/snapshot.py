"""Snapshot API models."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class SnapshotSummaryResponse(BaseModel):
    snapshot_id: str
    schema_version: str
    created_at: str
    topic_card_count: int
    evidence_index_count: int
    pedagogy_item_count: int
    available: bool = True


class SnapshotDetailResponse(BaseModel):
    snapshot_id: str
    manifest: dict[str, Any]
    build_report: dict[str, Any]
    counts: dict[str, int]
    validation_ok: bool
