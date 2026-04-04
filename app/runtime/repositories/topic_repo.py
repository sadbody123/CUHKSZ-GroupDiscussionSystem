"""Topic card repository (read-only)."""

from __future__ import annotations

from app.schemas.topic_card import TopicCard


class TopicRepository:
    def __init__(self, cards: list[TopicCard]) -> None:
        self._by_id: dict[str, TopicCard] = {c.topic_id: c for c in cards}

    def list_topics(self) -> list[TopicCard]:
        return list(self._by_id.values())

    def get_topic(self, topic_id: str) -> TopicCard | None:
        return self._by_id.get(topic_id)

    def search_topics(self, keyword: str) -> list[TopicCard]:
        k = keyword.lower().strip()
        if not k:
            return self.list_topics()
        out: list[TopicCard] = []
        for c in self._by_id.values():
            blob = f"{c.topic} {c.summary or ''} {' '.join(c.tags)}".lower()
            if k in blob:
                out.append(c)
        return out
