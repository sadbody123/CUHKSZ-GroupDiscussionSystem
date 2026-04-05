"""Local review queue."""

from __future__ import annotations

from pydantic import BaseModel, Field


class ReviewQueueItem(BaseModel):
    queue_item_id: str
    review_pack_id: str
    session_id: str
    reviewer_id: str | None = None
    status: str
    priority: str | None = None
    created_at: str
    updated_at: str | None = None
    metadata: dict = Field(default_factory=dict)
