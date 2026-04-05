"""Review export / summary helpers."""

from __future__ import annotations

from pydantic import BaseModel, Field


class HumanReview(BaseModel):
    review_id: str
    review_pack_id: str
    reviewer_id: str
    created_at: str
    rubric_scores: list[dict] = Field(default_factory=list)
    annotations: list[dict] = Field(default_factory=list)
    override_decisions: list[dict] = Field(default_factory=list)
    overall_judgment: str | None = None
    summary_notes: list[str] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)


class ReviewedOutputArtifact(BaseModel):
    """New artifact; does not replace originals."""

    artifact_kind: str = "reviewed_feedback"
    review_id: str
    reviewer_id: str
    review_pack_id: str
    session_id: str
    created_at: str
    source: str = "human_review_merge"
    proxy_note: str | None = None
    payload: dict = Field(default_factory=dict)
    metadata: dict = Field(default_factory=dict)
