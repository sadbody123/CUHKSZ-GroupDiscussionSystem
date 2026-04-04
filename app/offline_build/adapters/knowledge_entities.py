"""Adapter: knowledge_entities table."""

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


def _entity_text(record: dict[str, Any]) -> str | None:
    name = first_str(record, "name", "title", "label", "canonical_name")
    body = first_text(record)
    if body:
        if name and name not in body[:200]:
            return f"{name}\n\n{body}"
        return body
    if name:
        return name
    return None


class KnowledgeEntitiesAdapter(BaseAdapter):
    table_name = "knowledge_entities"

    def normalize_record(
        self,
        record: dict[str, Any],
        file_name: str | None = None,
    ) -> NormalizedDocument | None:
        text = _entity_text(record)
        if not text:
            return None
        doc_id = stable_doc_id(self.table_name, record)
        source_id = first_str(record, "id", "_id", "uuid", "entity_id", "slug")
        title = first_str(record, "name", "title", "label", "canonical_name")
        exclude = {
            "id",
            "_id",
            "name",
            "title",
            "label",
            "content",
            "body",
            "text",
            "description",
            "summary",
        }
        meta = metadata_passthrough(record, exclude=exclude)
        if file_name:
            meta["upstream_file"] = file_name
        return NormalizedDocument(
            doc_id=doc_id,
            source_table=self.table_name,
            source_id=source_id,
            title=title,
            url=first_str(record, "url", "link", "wikipedia_url"),
            published_at=first_str(record, "updated_at", "created_at"),
            language=first_str(record, "language", "lang"),
            clean_text=text,
            source_type=default_source_type_for_table(self.table_name),
            raw_record_ref=source_id,
            metadata=meta,
        )
