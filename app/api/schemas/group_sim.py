"""API models for group simulation."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class RosterTemplateSummaryResponse(BaseModel):
    roster_template_id: str
    display_name: str
    total_participants: int = 4
    team_count: int = 2


class RosterTemplateDetailResponse(BaseModel):
    roster_template_id: str
    display_name: str
    description: str | None = None
    total_participants: int = 4
    team_count: int = 2
    participants: list[dict[str, Any]] = Field(default_factory=list)
    teams: list[dict[str, Any]] = Field(default_factory=list)
    recommended_mode_ids: list[str] = Field(default_factory=list)
    default_assessment_template_id: str | None = None
    simulation_note: str = ""


class SessionRosterResponse(BaseModel):
    session_id: str
    roster_template_id: str | None = None
    user_participant_id: str | None = None
    participants: list[dict[str, Any]] = Field(default_factory=list)
    teams: list[dict[str, Any]] = Field(default_factory=list)
    simulation_note: str = ""


class GroupBalanceResponse(BaseModel):
    report_id: str | None = None
    session_id: str = ""
    roster_template_id: str | None = None
    created_at: str = ""
    participant_stats: list[dict[str, Any]] = Field(default_factory=list)
    team_stats: list[dict[str, Any]] = Field(default_factory=list)
    balance_flags: list[dict[str, Any]] = Field(default_factory=list)
    strengths: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class ParticipantSummaryResponse(BaseModel):
    participant_id: str
    display_name: str | None = None
    team_id: str | None = None
    relation_to_user: str | None = None
    turn_count: int = 0


class GroupReportResponse(BaseModel):
    roster: dict[str, Any] = Field(default_factory=dict)
    balance: dict[str, Any] = Field(default_factory=dict)
    simulation_note: str = ""
