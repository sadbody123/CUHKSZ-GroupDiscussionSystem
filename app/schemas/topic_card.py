"""Topic cards for discussion practice (manual + bootstrap)."""

from __future__ import annotations

from pydantic import BaseModel, Field, model_validator


class TopicCard(BaseModel):
    """Training topic card with stances, hints, and links to evidence."""

    topic_id: str
    topic: str = ""
    summary: str | None = None
    stance_for: str | None = None
    stance_against: str | None = None
    core_points_for: list[str] = Field(default_factory=list)
    core_points_against: list[str] = Field(default_factory=list)
    example_hints: list[str] = Field(default_factory=list)
    common_questions: list[str] = Field(default_factory=list)
    pitfalls: list[str] = Field(default_factory=list)
    related_doc_ids: list[str] = Field(default_factory=list)
    related_chunk_ids: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)
    title: str | None = None

    @model_validator(mode="after")
    def _ensure_topic_label(self) -> TopicCard:
        if not self.topic and self.title:
            self.topic = self.title
        return self
