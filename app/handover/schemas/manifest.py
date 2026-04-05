"""Release manifest."""

from __future__ import annotations

from pydantic import BaseModel, Field


class ReleaseManifest(BaseModel):
    release_id: str
    release_version: str
    profile_id: str
    created_at: str
    rc_report_ref: str | None = None
    readiness_report_ref: str | None = None
    stability_report_ref: str | None = None
    capability_matrix_ref: str | None = None
    active_snapshot_ids: list[str] = Field(default_factory=list)
    active_demo_scenario_ids: list[str] = Field(default_factory=list)
    included_component_areas: list[str] = Field(default_factory=list)
    included_artifact_refs: dict = Field(default_factory=dict)
    known_limitations_ref: str | None = None
    docs_bundle_ref: str | None = None
    metadata: dict = Field(default_factory=dict)
