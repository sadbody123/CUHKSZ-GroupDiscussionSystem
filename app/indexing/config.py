"""Indexing config helpers."""

from __future__ import annotations

from typing import Any


def retrieval_section(profile_retrieval: dict[str, Any] | None) -> dict[str, Any]:
    r = dict(profile_retrieval or {})
    r.setdefault("mode", "rule")
    r.setdefault("use_indexes_if_available", True)
    r.setdefault("lexical_top_k", 20)
    r.setdefault("vector_top_k", 20)
    r.setdefault("final_top_k", 8)
    r.setdefault("lexical_weight", 0.5)
    r.setdefault("vector_weight", 0.5)
    r.setdefault("title_boost", 1.25)
    r.setdefault("topic_tag_boost", 1.15)
    r.setdefault("quality_boost", 0.15)
    r.setdefault("credibility_boost", 0.15)
    return r
