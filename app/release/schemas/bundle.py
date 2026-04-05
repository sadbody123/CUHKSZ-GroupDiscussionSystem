"""Demo bundle manifest."""

from __future__ import annotations

from pydantic import BaseModel, Field


class DemoBundleManifest(BaseModel):
    bundle_id: str
    profile_id: str
    created_at: str
    included_reports: list[str] = Field(default_factory=list)
    included_scenarios: list[str] = Field(default_factory=list)
    included_artifacts: list[str] = Field(default_factory=list)
    output_paths: dict = Field(default_factory=dict)
    notes: list[str] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)
