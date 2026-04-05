"""Roster template catalog (read-only)."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_group_service
from app.api.schemas.group_sim import RosterTemplateDetailResponse, RosterTemplateSummaryResponse
from app.application.group_service import GroupService
from app.group_sim.constants import GROUP_PRACTICE_NOTE

router = APIRouter(tags=["group_sim"])


@router.get("/roster-templates", response_model=list[RosterTemplateSummaryResponse])
def list_roster_templates(gsvc: Annotated[GroupService, Depends(get_group_service)]) -> list[RosterTemplateSummaryResponse]:
    rows = gsvc.list_roster_templates()
    return [RosterTemplateSummaryResponse(**r) for r in rows]


@router.get("/roster-templates/{roster_template_id}", response_model=RosterTemplateDetailResponse)
def get_roster_template(
    roster_template_id: str,
    gsvc: Annotated[GroupService, Depends(get_group_service)],
) -> RosterTemplateDetailResponse:
    r = gsvc.get_roster_template(roster_template_id)
    if not r:
        raise HTTPException(status_code=404, detail="roster template not found")
    return RosterTemplateDetailResponse(
        roster_template_id=r["roster_template_id"],
        display_name=r.get("display_name") or roster_template_id,
        description=r.get("description"),
        total_participants=int(r.get("total_participants") or 0),
        team_count=int(r.get("team_count") or 0),
        participants=list(r.get("participants") or []),
        teams=list(r.get("teams") or []),
        recommended_mode_ids=list(r.get("recommended_mode_ids") or []),
        default_assessment_template_id=r.get("default_assessment_template_id"),
        simulation_note=GROUP_PRACTICE_NOTE,
    )
