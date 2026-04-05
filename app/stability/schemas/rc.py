"""Release candidate report."""

from __future__ import annotations

from pydantic import BaseModel, Field


class ReleaseCandidateReport(BaseModel):
    rc_report_id: str
    profile_id: str
    created_at: str
    readiness_status: str
    gating_checks: list[dict] = Field(default_factory=list)
    blocking_issue_ids: list[str] = Field(default_factory=list)
    accepted_limitations: list[str] = Field(default_factory=list)
    demo_matrix_summary: dict = Field(default_factory=dict)
    stability_summary: dict = Field(default_factory=dict)
    docs_status: dict = Field(default_factory=dict)
    go_no_go: str
    metadata: dict = Field(default_factory=dict)
