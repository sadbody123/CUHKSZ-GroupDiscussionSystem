"""Snapshot manifest and build report."""

from __future__ import annotations

from pydantic import BaseModel, Field


class SnapshotManifest(BaseModel):
    """Index for an offline knowledge snapshot."""

    snapshot_id: str
    schema_version: str = "1.0"
    created_at: str
    input_tables: list[str] = Field(default_factory=list)
    normalized_doc_count: int = 0
    evidence_chunk_count: int = 0
    deduped_doc_count: int = 0
    pedagogy_item_count: int = 0
    topic_card_count: int = 0
    evidence_index_count: int = 0
    notes: list[str] | None = None


class BuildReport(BaseModel):
    """Human-readable build statistics."""

    input_file_count: int = 0
    records_read: int = 0
    normalized_success: int = 0
    dropped: int = 0
    pre_dedupe_count: int = 0
    post_dedupe_count: int = 0
    near_dup_removed_count: int = 0
    near_dup_clusters: int = 0
    chunk_count: int = 0
    tables_used: list[str] = Field(default_factory=list)
    pedagogy_files_read: int = 0
    pedagogy_lines_read: int = 0
    pedagogy_items_out: int = 0
    topic_card_files_read: int = 0
    topic_cards_manual: int = 0
    topic_cards_bootstrapped: int = 0
    topic_cards_out: int = 0
    evidence_index_count: int = 0
