"""Minimal keyword rules for topic tags."""

from __future__ import annotations

import re

_RULES: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"\b(ai|机器学习|deep learning|llm|人工智能)\b", re.I), "ai"),
    (re.compile(r"\b(研究|research|科研)\b", re.I), "research"),
    (re.compile(r"\b(校园|大学|university|campus)\b", re.I), "campus"),
    (re.compile(r"\b(活动|event|讲座|workshop)\b", re.I), "events"),
    (re.compile(r"\b(数据|database|dataset)\b", re.I), "data"),
]


def infer_topic_tags(title: str | None, text: str, max_tags: int = 8) -> list[str]:
    blob = f"{title or ''}\n{text[:4000]}"
    tags: list[str] = []
    seen: set[str] = set()
    for pat, label in _RULES:
        if pat.search(blob) and label not in seen:
            tags.append(label)
            seen.add(label)
        if len(tags) >= max_tags:
            break
    return tags
