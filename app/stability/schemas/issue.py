"""Issue records."""

from __future__ import annotations

from pydantic import BaseModel, Field


class IssueRecord(BaseModel):
    issue_id: str
    source_type: str
    severity: str
    area: str
    title: str
    description: str = ""
    reproducible: bool | None = None
    status: str = "open"
    linked_refs: list[str] = Field(default_factory=list)
    suggested_fix: str | None = None
    metadata: dict = Field(default_factory=dict)
