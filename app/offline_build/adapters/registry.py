"""Registry of table → adapter."""

from __future__ import annotations

from typing import Iterable

from app.offline_build.adapters.base import BaseAdapter
from app.offline_build.adapters.community_articles import CommunityArticlesAdapter
from app.offline_build.adapters.community_events import CommunityEventsAdapter
from app.offline_build.adapters.community_pages import CommunityPagesAdapter
from app.offline_build.adapters.encyclopedia_entries import EncyclopediaEntriesAdapter
from app.offline_build.adapters.knowledge_entities import KnowledgeEntitiesAdapter
from app.offline_build.adapters.reports import ReportsAdapter
from app.offline_build.adapters.research_outputs import ResearchOutputsAdapter
from app.offline_build.adapters.research_projects import ResearchProjectsAdapter

_ADAPTERS: tuple[type[BaseAdapter], ...] = (
    ReportsAdapter,
    ResearchOutputsAdapter,
    KnowledgeEntitiesAdapter,
    ResearchProjectsAdapter,
    EncyclopediaEntriesAdapter,
    CommunityArticlesAdapter,
    CommunityPagesAdapter,
    CommunityEventsAdapter,
)

_INSTANCES: dict[str, BaseAdapter] = {cls.table_name: cls() for cls in _ADAPTERS}

SUPPORTED_TABLES: frozenset[str] = frozenset(_INSTANCES.keys())


def get_adapter(table_name: str) -> BaseAdapter | None:
    return _INSTANCES.get(table_name.lower().strip())


def iter_adapters() -> Iterable[BaseAdapter]:
    return _INSTANCES.values()
