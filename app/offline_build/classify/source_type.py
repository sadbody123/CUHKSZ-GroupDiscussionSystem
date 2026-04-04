"""Map upstream table names to coarse source_type labels."""

from __future__ import annotations

_TABLE_TO_SOURCE: dict[str, str] = {
    "reports": "official_report",
    "research_outputs": "research",
    "knowledge_entities": "knowledge",
    "research_projects": "research",
    "encyclopedia_entries": "encyclopedia",
    "community_articles": "community",
    "community_pages": "community",
    "community_events": "community",
}


def default_source_type_for_table(table_name: str) -> str:
    return _TABLE_TO_SOURCE.get(table_name.lower().strip(), "unknown")
