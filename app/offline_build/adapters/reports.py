"""Adapter: reports table."""

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


class ReportsAdapter(BaseAdapter):
    table_name = "reports"

    def normalize_record(
        self,
        record: dict[str, Any],
        file_name: str | None = None,
    ) -> NormalizedDocument | None:
        text = first_text(record) or first_str(record, "title", "name", "headline")
        if not text:
            return None
        doc_id = stable_doc_id(self.table_name, record)
        source_id = first_str(record, "id", "_id", "uuid", "report_id")
        title = first_str(record, "title", "name", "subject", "headline")
        exclude = {
            "id",
            "_id",
            "uuid",
            "title",
            "name",
            "subject",
            "headline",
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
            url=first_str(record, "url", "link", "source_url", "permalink"),
            published_at=first_str(
                record,
                "published_at",
                "created_at",
                "updated_at",
                "date",
                "issued_at",
            ),
            language=first_str(record, "language", "lang", "locale"),
            clean_text=text,
            source_type=default_source_type_for_table(self.table_name),
            raw_record_ref=source_id,
            metadata=meta,
        )
