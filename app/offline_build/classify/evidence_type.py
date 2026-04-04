"""Rule-based evidence_type from table + text heuristics."""

from __future__ import annotations

import re


def infer_evidence_type(table_name: str, title: str | None, text: str) -> str:
    t = table_name.lower().strip()
    low = f"{title or ''} {text}".lower()

    if t == "reports":
        return "report"
    if t == "research_outputs":
        return "publication"
    if t == "knowledge_entities":
        return "entity"
    if t == "research_projects":
        return "project"
    if t == "encyclopedia_entries":
        return "article"
    if t == "community_articles":
        return "article"
    if t == "community_pages":
        return "page"
    if t == "community_events":
        if re.search(r"\b(workshop|seminar|讲座|研讨会)\b", low):
            return "event"
        return "event"

    if "http" in text[:200] or "www." in low:
        return "page"
    return "article"
