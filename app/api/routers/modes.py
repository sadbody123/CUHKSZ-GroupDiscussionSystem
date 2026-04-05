"""Practice modes, presets, assessment templates (read-only catalog)."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_mode_service
from app.api.schemas.mode import (
    AssessmentTemplateResponse,
    ModeDetailResponse,
    ModeSummaryResponse,
    PresetDetailResponse,
    PresetSummaryResponse,
)
from app.application.mode_service import ModeService

router = APIRouter(tags=["modes"])


@router.get("/modes", response_model=list[ModeSummaryResponse])
def list_modes(svc: Annotated[ModeService, Depends(get_mode_service)]) -> list[ModeSummaryResponse]:
    rows = svc.list_modes()
    out: list[ModeSummaryResponse] = []
    for r in rows:
        out.append(
            ModeSummaryResponse(
                mode_id=r["mode_id"],
                mode_type=r["mode_type"],
                display_name=r["display_name"],
                tags=list(r.get("tags") or []),
            )
        )
    return out


@router.get("/modes/{mode_id}", response_model=ModeDetailResponse)
def get_mode(mode_id: str, svc: Annotated[ModeService, Depends(get_mode_service)]) -> ModeDetailResponse:
    r = svc.get_mode(mode_id)
    if not r:
        raise HTTPException(status_code=404, detail="mode not found")
    return ModeDetailResponse.model_validate(r)


@router.get("/presets", response_model=list[PresetSummaryResponse])
def list_presets(svc: Annotated[ModeService, Depends(get_mode_service)]) -> list[PresetSummaryResponse]:
    rows = svc.list_presets()
    return [
        PresetSummaryResponse(
            preset_id=r["preset_id"],
            mode_id=r["mode_id"],
            display_name=r["display_name"],
            tags=list(r.get("tags") or []),
        )
        for r in rows
    ]


@router.get("/presets/{preset_id}", response_model=PresetDetailResponse)
def get_preset(preset_id: str, svc: Annotated[ModeService, Depends(get_mode_service)]) -> PresetDetailResponse:
    r = svc.get_preset(preset_id)
    if not r:
        raise HTTPException(status_code=404, detail="preset not found")
    return PresetDetailResponse.model_validate(r)


@router.get("/assessment-templates", response_model=list[AssessmentTemplateResponse])
def list_assessment_templates(
    svc: Annotated[ModeService, Depends(get_mode_service)],
) -> list[AssessmentTemplateResponse]:
    from app.modes.constants import SIMULATION_NOTE

    rows = svc.list_assessment_templates()
    out: list[AssessmentTemplateResponse] = []
    for r in rows:
        out.append(
            AssessmentTemplateResponse(
                template_id=r["template_id"],
                display_name=r["display_name"],
                description=r.get("description"),
                simulated_group_size=int(r.get("simulated_group_size") or 4),
                prep_seconds=r.get("prep_seconds"),
                discussion_seconds=int(r.get("discussion_seconds") or 0),
                metadata=dict(r.get("metadata") or {}),
                simulation_note=SIMULATION_NOTE,
            )
        )
    return out


@router.get("/assessment-templates/{template_id}", response_model=AssessmentTemplateResponse)
def get_assessment_template(
    template_id: str,
    svc: Annotated[ModeService, Depends(get_mode_service)],
) -> AssessmentTemplateResponse:
    from app.modes.constants import SIMULATION_NOTE

    r = svc.get_assessment_template(template_id)
    if not r:
        raise HTTPException(status_code=404, detail="template not found")
    return AssessmentTemplateResponse(
        template_id=r["template_id"],
        display_name=r["display_name"],
        description=r.get("description"),
        simulated_group_size=int(r.get("simulated_group_size") or 4),
        prep_seconds=r.get("prep_seconds"),
        discussion_seconds=int(r.get("discussion_seconds") or 0),
        metadata=dict(r.get("metadata") or {}),
        simulation_note=SIMULATION_NOTE,
    )
