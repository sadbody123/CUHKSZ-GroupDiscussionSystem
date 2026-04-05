"""Review pack aggregate."""

from __future__ import annotations

from pydantic import BaseModel, Field


class ReviewPack(BaseModel):
    review_pack_id: str
    session_id: str
    learner_id: str | None = None
    topic_id: str | None = None
    mode_id: str | None = None
    roster_template_id: str | None = None
    created_at: str
    status: str
    included_artifacts: dict = Field(default_factory=dict)
    ai_summary: dict = Field(default_factory=dict)
    transcript_ref: str | None = None
    proxy_limitations: list[str] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)
