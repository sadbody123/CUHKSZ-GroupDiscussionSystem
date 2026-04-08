"""Review item schema for runtime V2 quality interruptions."""

from __future__ import annotations

from pydantic import BaseModel, Field


class ReviewItem(BaseModel):
    review_id: str
    session_id: str
    run_id: str
    checkpoint_id: str | None = None
    topic_id: str | None = None
    reason: str | None = None
    interrupt_reason: str | None = None
    quality_flags: list[str] = Field(default_factory=list)
    draft_reply_text: str | None = None
    draft_reply_summary: str | None = None
    status: str = "pending"  # pending | approved | rejected | resumed | resolved
    version: int = 1
    allowed_actions: list[str] = Field(default_factory=list)
    review_decision_payload: dict = Field(default_factory=dict)
    resolved_by: str | None = None
    updated_by: str | None = None
    notes: list[str] = Field(default_factory=list)
    created_at: str
    updated_at: str
    metadata: dict = Field(default_factory=dict)
