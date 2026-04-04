"""Lightweight filter helpers (no embeddings)."""

from __future__ import annotations

from app.schemas.evidence_index import EvidenceIndexItem


def keyword_hits(text: str, keyword: str) -> int:
    if not keyword.strip():
        return 0
    low = text.lower()
    k = keyword.lower().strip()
    return low.count(k)


def stance_supportive(hint: str | None) -> bool:
    return (hint or "").lower() in ("for", "neutral", "unknown", "")


def stance_challenging(hint: str | None) -> bool:
    return (hint or "").lower() in ("against", "mixed", "neutral", "unknown", "")


def evidence_matches_topic_tag(ev: EvidenceIndexItem, tag: str) -> bool:
    t = tag.lower().strip()
    return any(t == x.lower() for x in ev.topic_tags)
