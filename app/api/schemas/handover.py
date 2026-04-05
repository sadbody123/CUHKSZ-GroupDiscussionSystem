"""Handover API response models."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ReleaseManifestResponse(BaseModel):
    manifest: dict[str, Any]


class BillOfMaterialsResponse(BaseModel):
    bom: dict[str, Any]
    entry_count: int
    warning_count: int


class DemoKitResponse(BaseModel):
    demo_kit_id: str | None = None
    target_profile_id: str | None = None
    demo_scenario_ids: list[str] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)


class AcceptanceEvidenceResponse(BaseModel):
    evidence: dict[str, Any]


class DeliveryVerificationResponse(BaseModel):
    report: dict[str, Any]


class HandoverKitResponse(BaseModel):
    handover_kit_id: str | None = None
    notes: list[str] = Field(default_factory=list)
    target_audience: str | None = None


class FinalReleaseSummaryResponse(BaseModel):
    summary: dict[str, Any]
