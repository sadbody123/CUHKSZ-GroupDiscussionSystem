"""Construct SnapshotManifest objects."""

from __future__ import annotations

from datetime import datetime, timezone

from app.schemas.snapshot import SnapshotManifest


def build_manifest(
    *,
    snapshot_id: str,
    input_tables: list[str],
    normalized_doc_count: int,
    evidence_chunk_count: int,
    deduped_doc_count: int,
    notes: list[str] | None = None,
    pedagogy_item_count: int = 0,
    topic_card_count: int = 0,
    evidence_index_count: int = 0,
    schema_version: str = "1.0",
) -> SnapshotManifest:
    created = datetime.now(timezone.utc).isoformat()
    return SnapshotManifest(
        snapshot_id=snapshot_id,
        schema_version=schema_version,
        created_at=created,
        input_tables=sorted(set(input_tables)),
        normalized_doc_count=normalized_doc_count,
        evidence_chunk_count=evidence_chunk_count,
        deduped_doc_count=deduped_doc_count,
        pedagogy_item_count=pedagogy_item_count,
        topic_card_count=topic_card_count,
        evidence_index_count=evidence_index_count,
        notes=notes,
    )
