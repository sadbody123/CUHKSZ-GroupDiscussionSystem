"""Adapter: community_events table."""

from __future__ import annotations

from typing import Any

from app.offline_build.adapters.base import (
    BaseAdapter,
    first_str,
    first_text,
    metadata_passthrough,
    stable_doc_id,
)
from app.offline_build.classify.source_type import default_source_type_for_table
from app.schemas.normalized_doc import NormalizedDocument


def _event_text(record: dict[str, Any]) -> str | None:
    chunks: list[str] = []
    head = first_str(record, "title", "name")
    if head:
        chunks.append(head)
    body = first_text(record)
    if body:
        chunks.append(body)
    for key in ("summary", "description", "location", "venue", "address"):
        v = record.get(key)
        if v is not None and str(v).strip():
            chunks.append(f"{key}: {str(v).strip()}")
    for key in ("start_time", "ends_at", "starts_at", "end_time"):
        v = record.get(key)
        if v is not None and str(v).strip():
            chunks.append(f"{key}: {str(v).strip()}")
    out = "\n\n".join([c for c in chunks if c])
    return out if out else None


class CommunityEventsAdapter(BaseAdapter):
    table_name = "community_events"

    def normalize_record(
        self,
        record: dict[str, Any],
        file_name: str | None = None,
    ) -> NormalizedDocument | None:
        text = _event_text(record)
        if not text:
            return None
        doc_id = stable_doc_id(self.table_name, record)
        source_id = first_str(record, "id", "_id", "uuid", "event_id", "slug")
        title = first_str(record, "title", "name", "summary")
        exclude = {
            "id",
            "_id",
            "title",
            "name",
            "summary",
            "description",
            "content",
            "body",
            "text",
            "location",
            "venue",
            "address",
        }
        meta = metadata_passthrough(record, exclude=exclude)
        if file_name:
            meta["upstream_file"] = file_name
        return NormalizedDocument(
            doc_id=doc_id,
            source_table=self.table_name,
            source_id=source_id,
            title=title,
            url=first_str(record, "url", "link", "registration_url"),
            published_at=first_str(
                record,
                "start_time",
                "starts_at",
                "date",
                "created_at",
            ),
            language=first_str(record, "language", "lang"),
            clean_text=text,
            source_type=default_source_type_for_table(self.table_name),
            raw_record_ref=source_id,
            metadata=meta,
        )
