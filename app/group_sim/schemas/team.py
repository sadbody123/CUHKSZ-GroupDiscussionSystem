"""Team specs."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class TeamSpec(BaseModel):
    team_id: str
    stance: str = ""
    display_name: str = ""
    participant_ids: list[str] = Field(default_factory=list)
    intro_participant_id: str | None = None
    summary_participant_id: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
