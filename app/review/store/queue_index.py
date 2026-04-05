"""Minimal JSON queue index."""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

from app.review.constants import QUEUE_ASSIGNED, QUEUE_DONE, QUEUE_OPEN
from app.review.schemas.queue import ReviewQueueItem


class QueueIndex:
    def __init__(self, path: Path, max_items: int = 500) -> None:
        self._path = path.resolve()
        self._max = max_items
        self._path.parent.mkdir(parents=True, exist_ok=True)

    def _load(self) -> list[dict]:
        if not self._path.is_file():
            return []
        try:
            raw = json.loads(self._path.read_text(encoding="utf-8"))
            return raw if isinstance(raw, list) else []
        except (OSError, json.JSONDecodeError):
            return []

    def _save(self, rows: list[dict]) -> None:
        self._path.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    def enqueue_pack(
        self,
        *,
        review_pack_id: str,
        session_id: str,
        priority: str | None = None,
        metadata: dict | None = None,
    ) -> ReviewQueueItem:
        rows = self._load()
        now = datetime.now(timezone.utc).isoformat()
        item = ReviewQueueItem(
            queue_item_id=str(uuid.uuid4()),
            review_pack_id=review_pack_id,
            session_id=session_id,
            reviewer_id=None,
            status=QUEUE_OPEN,
            priority=priority,
            created_at=now,
            updated_at=now,
            metadata=metadata or {},
        )
        rows.append(item.model_dump())
        if len(rows) > self._max:
            rows = rows[-self._max :]
        self._save(rows)
        return item

    def assign_reviewer(self, queue_item_id: str, reviewer_id: str) -> ReviewQueueItem | None:
        rows = self._load()
        now = datetime.now(timezone.utc).isoformat()
        for i, row in enumerate(rows):
            if row.get("queue_item_id") == queue_item_id:
                row["reviewer_id"] = reviewer_id
                row["status"] = QUEUE_ASSIGNED
                row["updated_at"] = now
                rows[i] = row
                self._save(rows)
                return ReviewQueueItem.model_validate(row)
        return None

    def update_status(self, queue_item_id: str, status: str) -> ReviewQueueItem | None:
        rows = self._load()
        now = datetime.now(timezone.utc).isoformat()
        for i, row in enumerate(rows):
            if row.get("queue_item_id") == queue_item_id:
                row["status"] = status
                row["updated_at"] = now
                rows[i] = row
                self._save(rows)
                return ReviewQueueItem.model_validate(row)
        return None

    def list_queue_items(
        self,
        *,
        status: str | None = None,
        reviewer_id: str | None = None,
        session_id: str | None = None,
    ) -> list[ReviewQueueItem]:
        out: list[ReviewQueueItem] = []
        for row in self._load():
            try:
                it = ReviewQueueItem.model_validate(row)
            except Exception:
                continue
            if status and it.status != status:
                continue
            if reviewer_id and it.reviewer_id != reviewer_id:
                continue
            if session_id and it.session_id != session_id:
                continue
            out.append(it)
        return sorted(out, key=lambda x: x.created_at, reverse=True)
