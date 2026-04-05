"""Release profile."""

from __future__ import annotations

from pydantic import BaseModel, Field


class ReleaseProfile(BaseModel):
    profile_id: str
    display_name: str
    description: str | None = None
    created_at: str | None = None
    enabled_capabilities: list[str] = Field(default_factory=list)
    disabled_capabilities: list[str] = Field(default_factory=list)
    experimental_capabilities: list[str] = Field(default_factory=list)
    default_snapshot_requirements: dict = Field(default_factory=dict)
    default_provider_policy: dict = Field(default_factory=dict)
    default_runtime_profile_policy: dict = Field(default_factory=dict)
    ui_visibility_policy: dict = Field(default_factory=dict)
    api_visibility_policy: dict = Field(default_factory=dict)
    demo_scenario_ids: list[str] = Field(default_factory=list)
    acceptance_checks: list[str] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)
