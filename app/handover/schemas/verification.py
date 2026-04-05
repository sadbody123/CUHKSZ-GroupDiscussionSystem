"""Delivery verification."""

from __future__ import annotations

from pydantic import BaseModel, Field


class DeliveryVerificationReport(BaseModel):
    verification_id: str
    created_at: str
    release_id: str | None = None
    profile_id: str | None = None
    overall_status: str
    checks: list[dict] = Field(default_factory=list)
    failed_steps: list[str] = Field(default_factory=list)
    suggested_fixes: list[str] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)
