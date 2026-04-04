"""Soft validation helpers for pedagogy JSONL rows."""

from __future__ import annotations

from typing import Any

from app.schemas.pedagogy import PedagogyItem


def row_to_pedagogy_item(raw: dict[str, Any], *, default_item_type: str) -> PedagogyItem | None:
    """Build PedagogyItem from a dict; return None if unusable."""
    content = raw.get("content")
    if content is None or not str(content).strip():
        return None
    iid = raw.get("item_id") or raw.get("id") or raw.get("uuid")
    if not iid:
        return None
    item_type = str(raw.get("item_type") or default_item_type).strip() or default_item_type
    tags = raw.get("tags")
    if not isinstance(tags, list):
        tags = []
    meta = raw.get("metadata")
    if not isinstance(meta, dict):
        meta = {}
    return PedagogyItem(
        item_id=str(iid),
        item_type=item_type,
        category=_opt_str(raw.get("category")),
        subcategory=_opt_str(raw.get("subcategory")),
        content=str(content).strip(),
        language=_opt_str(raw.get("language")),
        source_ref=_opt_str(raw.get("source_ref")),
        tags=[str(t) for t in tags if t is not None],
        metadata=meta,
    )


def _opt_str(v: Any) -> str | None:
    if v is None:
        return None
    s = str(v).strip()
    return s if s else None
