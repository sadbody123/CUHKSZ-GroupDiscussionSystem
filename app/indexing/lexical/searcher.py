"""Search lexical index."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.indexing.lexical.scoring import score_document


class LexicalSearcher:
    def __init__(self, index_path: Path) -> None:
        raw = json.loads(Path(index_path).read_text(encoding="utf-8"))
        self._docs: list[dict[str, Any]] = list(raw.get("docs") or [])

    @property
    def docs(self) -> list[dict[str, Any]]:
        return self._docs

    def search(
        self,
        query: str,
        *,
        top_k: int,
        query_tags: list[str] | None = None,
        title_boost: float = 1.25,
        topic_tag_boost: float = 1.15,
    ) -> list[tuple[str, float, dict[str, Any]]]:
        out: list[tuple[str, float, dict[str, Any]]] = []
        for d in self._docs:
            item_id = str(d.get("item_id") or "")
            text = str(d.get("text") or "")
            title = d.get("title")
            tags = list(d.get("tags") or [])
            sc = score_document(
                query,
                text,
                title=str(title) if title else None,
                doc_tags=tags,
                query_tags=query_tags or [],
                title_boost=title_boost,
                topic_tag_boost=topic_tag_boost,
            )
            out.append((item_id, sc, d))
        out.sort(key=lambda x: x[1], reverse=True)
        return out[:top_k]
