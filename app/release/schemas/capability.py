"""Capability descriptor."""

from __future__ import annotations

from pydantic import BaseModel, Field


class CapabilityDescriptor(BaseModel):
    capability_id: str
    display_name: str
    description: str | None = None
    area: str
    stability: str
    default_enabled: bool = True
    requires: list[str] = Field(default_factory=list)
    optional_requires: list[str] = Field(default_factory=list)
    related_artifact_kinds: list[str] = Field(default_factory=list)
    related_api_groups: list[str] = Field(default_factory=list)
    related_ui_panels: list[str] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)
