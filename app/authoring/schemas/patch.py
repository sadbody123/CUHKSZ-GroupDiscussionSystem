"""Patch proposal."""

from __future__ import annotations

from pydantic import BaseModel, Field


class PatchProposal(BaseModel):
    patch_id: str
    source_type: str
    source_ref_id: str | None = None
    target_artifact_type: str
    target_artifact_id: str
    title: str
    reason: str
    proposed_ops: list[dict] = Field(default_factory=list)
    evidence_refs: list[str] = Field(default_factory=list)
    confidence: float | None = None
    status: str = "proposed"
    metadata: dict = Field(default_factory=dict)
