"""Thin helpers for queue + pack status."""

from __future__ import annotations

from app.review.constants import QUEUE_ASSIGNED, QUEUE_DONE, QUEUE_OPEN
from app.review.store.queue_index import QueueIndex


def on_pack_opened(queue: QueueIndex, review_pack_id: str, session_id: str) -> None:
    for it in queue.list_queue_items(session_id=session_id):
        if it.review_pack_id == review_pack_id:
            queue.update_status(it.queue_item_id, QUEUE_ASSIGNED)
            return
    queue.enqueue_pack(review_pack_id=review_pack_id, session_id=session_id)


def on_pack_submitted(queue: QueueIndex, review_pack_id: str, session_id: str) -> None:
    for it in queue.list_queue_items(session_id=session_id):
        if it.review_pack_id == review_pack_id:
            queue.update_status(it.queue_item_id, QUEUE_DONE)
            return
