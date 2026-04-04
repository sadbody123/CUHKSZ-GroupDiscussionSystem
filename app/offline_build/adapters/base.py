"""Base adapter: map arbitrary upstream rows to NormalizedDocument."""

from __future__ import annotations

import hashlib
import json
from abc import ABC, abstractmethod
from typing import Any

from app.schemas.normalized_doc import NormalizedDocument


def first_str(record: dict[str, Any], *keys: str) -> str | None:
    for k in keys:
        v = record.get(k)
        if v is None:
            continue
        s = str(v).strip()
        if s:
            return s
    return None


def first_text(record: dict[str, Any]) -> str | None:
    """Collect primary text from common column names."""
    keys = (
        "content",
        "body",
        "text",
        "description",
        "summary",
        "abstract",
        "markdown",
        "html",
        "article_body",
        "main_text",
        "details",
        "notes",
    )
    for k in keys:
        v = record.get(k)
        if v is None:
            continue
        s = str(v).strip()
        if s:
            return s
    return None


def stable_doc_id(table_name: str, record: dict[str, Any]) -> str:
    sid = first_str(record, "id", "_id", "uuid", "pk", "slug")
    if sid:
        return f"{table_name}:{sid}"
    raw = json.dumps(record, sort_keys=True, default=str)
    h = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]
    return f"{table_name}:h{h}"


def metadata_passthrough(record: dict[str, Any], *, exclude: set[str]) -> dict[str, Any]:
    """Copy unknown / extra fields into metadata."""
    out: dict[str, Any] = {}
    for k, v in record.items():
        if k in exclude:
            continue
        try:
            json.dumps(v, default=str)
            out[k] = v
        except TypeError:
            out[k] = str(v)
    return out


class BaseAdapter(ABC):
    """One adapter per upstream table."""

    table_name: str

    @classmethod
    def can_handle(cls, table_name: str) -> bool:
        return table_name.lower().strip() == cls.table_name

    @abstractmethod
    def normalize_record(
        self,
        record: dict[str, Any],
        file_name: str | None = None,
    ) -> NormalizedDocument | None:
        """Return None if the row has no usable text."""
