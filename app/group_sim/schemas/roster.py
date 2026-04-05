"""Roster template."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class RosterTemplate(BaseModel):
    roster_template_id: str
    display_name: str = ""
    description: str | None = None
    total_participants: int = 4
    team_count: int = 2
    participants: list[dict[str, Any]] = Field(default_factory=list)
    teams: list[dict[str, Any]] = Field(default_factory=list)
    recommended_mode_ids: list[str] = Field(default_factory=list)
    default_assessment_template_id: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
