"""Demo kit."""

from __future__ import annotations

from pydantic import BaseModel, Field


class DemoKitManifest(BaseModel):
    demo_kit_id: str
    release_id: str
    created_at: str
    target_profile_id: str
    demo_scenario_ids: list[str] = Field(default_factory=list)
    sample_snapshot_id: str | None = None
    sample_session_refs: list[str] = Field(default_factory=list)
    sample_learner_refs: list[str] = Field(default_factory=list)
    sample_assignment_refs: list[str] = Field(default_factory=list)
    sample_review_refs: list[str] = Field(default_factory=list)
    sample_publication_refs: list[str] = Field(default_factory=list)
    quickstart_commands: list[str] = Field(default_factory=list)
    included_paths: list[str] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)
