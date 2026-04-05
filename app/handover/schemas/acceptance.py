"""Acceptance evidence."""

from __future__ import annotations

from pydantic import BaseModel, Field


class AcceptanceEvidence(BaseModel):
    evidence_id: str
    created_at: str
    release_id: str
    profile_id: str
    readiness_ref: str | None = None
    consistency_ref: str | None = None
    stability_ref: str | None = None
    rc_ref: str | None = None
    demo_result_refs: list[str] = Field(default_factory=list)
    passed_checks: list[dict] = Field(default_factory=list)
    failed_checks: list[dict] = Field(default_factory=list)
    accepted_limitations: list[str] = Field(default_factory=list)
    summary: dict = Field(default_factory=dict)
    metadata: dict = Field(default_factory=dict)
