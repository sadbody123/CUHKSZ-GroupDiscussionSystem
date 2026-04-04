"""Validate and normalize raw topic card dicts."""

from __future__ import annotations

from typing import Any

from app.schemas.topic_card import TopicCard


def dict_to_topic_card(raw: dict[str, Any]) -> TopicCard | None:
    tid = raw.get("topic_id") or raw.get("id")
    topic = raw.get("topic") or raw.get("title") or raw.get("name")
    if not tid or not topic:
        return None
    def _str_list(key: str) -> list[str]:
        v = raw.get(key)
        if v is None:
            return []
        if isinstance(v, list):
            return [str(x).strip() for x in v if x is not None and str(x).strip()]
        return []

    meta = raw.get("metadata")
    if not isinstance(meta, dict):
        meta = {}
    tags = raw.get("tags")
    if not isinstance(tags, list):
        tags = []
    return TopicCard(
        topic_id=str(tid).strip(),
        topic=str(topic).strip(),
        summary=_opt_str(raw.get("summary")),
        stance_for=_opt_str(raw.get("stance_for")),
        stance_against=_opt_str(raw.get("stance_against")),
        core_points_for=_str_list("core_points_for"),
        core_points_against=_str_list("core_points_against"),
        example_hints=_str_list("example_hints"),
        common_questions=_str_list("common_questions"),
        pitfalls=_str_list("pitfalls"),
        related_doc_ids=[str(x) for x in (raw.get("related_doc_ids") or []) if x],
        related_chunk_ids=[str(x) for x in (raw.get("related_chunk_ids") or []) if x],
        tags=[str(t) for t in tags if t is not None],
        metadata=meta,
        title=_opt_str(raw.get("title")),
    )


def _opt_str(v: Any) -> str | None:
    if v is None:
        return None
    s = str(v).strip()
    return s if s else None
