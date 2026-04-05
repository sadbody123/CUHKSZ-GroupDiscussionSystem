"""Publication record."""

from __future__ import annotations

from pydantic import BaseModel, Field


class PublicationRecord(BaseModel):
    publication_id: str
    draft_id: str
    artifact_type: str
    artifact_id: str
    published_version: str
    published_at: str
    published_by: str | None = None
    output_ref: str
    derivative_of: str | None = None
    validation_report_id: str | None = None
    preview_result_ids: list[str] = Field(default_factory=list)
    change_summary: list[str] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)
