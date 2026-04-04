"""Exact deduplication by hash of normalized clean_text."""

from __future__ import annotations

import hashlib
from typing import TypeVar

from app.schemas.normalized_doc import NormalizedDocument

T = TypeVar("T", bound=NormalizedDocument)


def _text_hash(clean_text: str) -> str:
    return hashlib.sha256(clean_text.encode("utf-8")).hexdigest()


def dedupe_by_text_hash(docs: list[NormalizedDocument]) -> tuple[list[NormalizedDocument], int]:
    """
    Keep first occurrence per clean_text hash.
    Returns (deduped_list, duplicate_count).
    """
    seen: set[str] = set()
    out: list[NormalizedDocument] = []
    dup = 0
    for d in docs:
        h = _text_hash(d.clean_text)
        if h in seen:
            dup += 1
            continue
        seen.add(h)
        out.append(d)
    return out, dup
