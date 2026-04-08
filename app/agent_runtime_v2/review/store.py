"""File-backed review item store for runtime V2."""

from __future__ import annotations

from pathlib import Path

from app.agent_runtime_v2.review.schemas import ReviewItem


class ReviewQueueStore:
    def __init__(self, root_dir: Path) -> None:
        self._root = root_dir
        self._root.mkdir(parents=True, exist_ok=True)

    def _path(self, review_id: str) -> Path:
        return self._root / f"{review_id}.json"

    def save(self, item: ReviewItem) -> Path:
        p = self._path(item.review_id)
        p.write_text(item.model_dump_json(indent=2) + "\n", encoding="utf-8")
        return p

    def load(self, review_id: str) -> ReviewItem | None:
        p = self._path(review_id)
        if not p.is_file():
            return None
        return ReviewItem.model_validate_json(p.read_text(encoding="utf-8"))

    def list(
        self,
        *,
        status: str | None = None,
        session_id: str | None = None,
        topic_id: str | None = None,
    ) -> list[ReviewItem]:
        out: list[ReviewItem] = []
        for f in sorted(self._root.glob("*.json")):
            try:
                item = ReviewItem.model_validate_json(f.read_text(encoding="utf-8"))
            except Exception:
                continue
            if status and item.status != status:
                continue
            if session_id and item.session_id != session_id:
                continue
            if topic_id and str(item.topic_id or "") != topic_id:
                continue
            out.append(item)
        return out
