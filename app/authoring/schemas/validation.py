"""Validation report schemas."""

from __future__ import annotations

from pydantic import BaseModel, Field


class ValidationFinding(BaseModel):
    finding_id: str
    severity: str
    rule_id: str
    message: str
    path: str | None = None
    suggested_fix: str | None = None
    metadata: dict = Field(default_factory=dict)


class ValidationReport(BaseModel):
    report_id: str
    draft_id: str
    created_at: str
    valid: bool
    findings: list[dict] = Field(default_factory=list)
    cross_ref_summary: dict = Field(default_factory=dict)
    lint_summary: dict = Field(default_factory=dict)
    metadata: dict = Field(default_factory=dict)
