"""Topic listing and detail from a snapshot."""

from __future__ import annotations

from app.application.config import AppConfig
from app.application.exceptions import TopicNotFoundError
from app.application.snapshot_service import SnapshotService
from app.runtime.retrieval.router import build_repositories
from app.runtime.snapshot_loader import load_snapshot


class TopicService:
    def __init__(self, config: AppConfig) -> None:
        self._config = config
        self._snapshots = SnapshotService(config)

    def list_topic_summaries(self, snapshot_id: str, keyword: str | None = None) -> list[dict]:
        path = self._snapshots.resolve_snapshot_dir(snapshot_id)
        b = load_snapshot(path)
        _ped, top, _ev, _doc, _src = build_repositories(b)
        cards = top.search_topics(keyword or "") if keyword else top.list_topics()
        out: list[dict] = []
        for c in cards:
            out.append(
                {
                    "topic_id": c.topic_id,
                    "topic": c.topic,
                    "summary": c.summary,
                    "tags": list(c.tags),
                }
            )
        return out

    def get_topic_detail(self, snapshot_id: str, topic_id: str) -> dict:
        path = self._snapshots.resolve_snapshot_dir(snapshot_id)
        b = load_snapshot(path)
        _ped, top, _ev, _doc, _src = build_repositories(b)
        card = top.get_topic(topic_id)
        if not card:
            raise TopicNotFoundError(topic_id)
        return card.model_dump()
