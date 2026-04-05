"""Lexical scoring (lightweight, deterministic)."""

from __future__ import annotations

import math
from typing import Any

from app.indexing.lexical.tokenizer import tokenize


def _tf(term: str, tokens: list[str]) -> float:
    c = sum(1 for t in tokens if t == term)
    return 1.0 + math.log1p(c) if c else 0.0


def score_document(
    query: str,
    doc_text: str,
    *,
    title: str | None = None,
    doc_tags: list[str] | None = None,
    query_tags: list[str] | None = None,
    title_boost: float = 1.25,
    topic_tag_boost: float = 1.15,
) -> float:
    q_terms = tokenize(query)
    if not q_terms:
        return 0.0
    body = tokenize((title or "") + " " + doc_text)
    title_toks = set(tokenize(title or ""))
    s = 0.0
    avg_idf_like = 1.0
    for qt in q_terms:
        tf_b = _tf(qt, body)
        if tf_b <= 0:
            continue
        w = avg_idf_like * tf_b
        if qt in title_toks:
            w *= title_boost
        s += w
    if doc_tags and query_tags:
        dt = {t.lower() for t in doc_tags}
        qt = {t.lower() for t in query_tags}
        if dt.intersection(qt):
            s *= topic_tag_boost
    return float(s)
