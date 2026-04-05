"""Handover kit."""

from __future__ import annotations

from pydantic import BaseModel, Field


class HandoverKitManifest(BaseModel):
    handover_kit_id: str
    release_id: str
    created_at: str
    target_audience: str = "local_operator"
    release_manifest_ref: str
    bom_ref: str
    demo_kit_ref: str | None = None
    acceptance_evidence_ref: str | None = None
    docs_refs: list[str] = Field(default_factory=list)
    script_refs: list[str] = Field(default_factory=list)
    included_output_paths: dict = Field(default_factory=dict)
    notes: list[str] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)
