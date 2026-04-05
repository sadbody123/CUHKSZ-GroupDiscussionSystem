"""Curriculum packs and assignment delivery API."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.deps import get_curriculum_service
from app.api.schemas.curriculum import (
    AssignmentDetailResponse,
    AssignmentProgressResponse,
    AssignmentReportResponse,
    AssignmentSummaryResponse,
    AttachSessionAttemptRequest,
    AttachSessionAttemptResponse,
    CreateAssignmentRequest,
    CurriculumPackDetailResponse,
    CurriculumPackFromPlanRequest,
    CurriculumPackSummaryResponse,
    LaunchAssignmentStepRequest,
    LaunchAssignmentStepResponse,
)
from app.application.curriculum_service import CurriculumService

router = APIRouter(tags=["curriculum"])


@router.get("/curriculum-packs", response_model=list[CurriculumPackSummaryResponse])
def list_packs(svc: Annotated[CurriculumService, Depends(get_curriculum_service)]) -> list[CurriculumPackSummaryResponse]:
    rows = svc.list_curriculum_packs()
    return [
        CurriculumPackSummaryResponse(
            pack_id=p.pack_id,
            display_name=p.display_name,
            version=p.version,
            target_skills=p.target_skills,
            tags=p.tags,
        )
        for p in rows
    ]


@router.get("/curriculum-packs/{pack_id}", response_model=CurriculumPackDetailResponse)
def get_pack(pack_id: str, svc: Annotated[CurriculumService, Depends(get_curriculum_service)]) -> CurriculumPackDetailResponse:
    try:
        p = svc.get_curriculum_pack(pack_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="pack not found") from None
    return CurriculumPackDetailResponse(
        pack_id=p.pack_id,
        display_name=p.display_name,
        description=p.description,
        author_id=p.author_id,
        version=p.version,
        target_skills=p.target_skills,
        steps=[s.model_dump() for s in p.steps],
        tags=p.tags,
        metadata=p.metadata,
    )


@router.post("/assignments", response_model=AssignmentDetailResponse)
def create_assignment(
    body: CreateAssignmentRequest,
    svc: Annotated[CurriculumService, Depends(get_curriculum_service)],
) -> AssignmentDetailResponse:
    try:
        a = svc.create_assignment(
            pack_id=body.pack_id,
            learner_ids=body.learner_ids,
            created_by=body.created_by,
            title=body.title,
            description=body.description,
            due_at=body.due_at,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    return AssignmentDetailResponse(**a.model_dump())


@router.get("/assignments", response_model=list[AssignmentSummaryResponse])
def list_assignments(
    svc: Annotated[CurriculumService, Depends(get_curriculum_service)],
    learner_id: str | None = Query(None),
) -> list[AssignmentSummaryResponse]:
    rows = svc.list_assignments(learner_id=learner_id)
    return [
        AssignmentSummaryResponse(
            assignment_id=a.assignment_id,
            title=a.title,
            pack_id=a.pack_id,
            status=a.status,
            learner_ids=a.learner_ids,
            created_at=a.created_at,
        )
        for a in rows
    ]


@router.get("/assignments/{assignment_id}", response_model=AssignmentDetailResponse)
def get_assignment(
    assignment_id: str,
    svc: Annotated[CurriculumService, Depends(get_curriculum_service)],
) -> AssignmentDetailResponse:
    try:
        a = svc.get_assignment(assignment_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="assignment not found") from None
    return AssignmentDetailResponse(**a.model_dump())


@router.get("/assignments/{assignment_id}/progress", response_model=AssignmentProgressResponse)
def assignment_progress(
    assignment_id: str,
    svc: Annotated[CurriculumService, Depends(get_curriculum_service)],
) -> AssignmentProgressResponse:
    try:
        d = svc.get_assignment_progress(assignment_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="assignment not found") from None
    return AssignmentProgressResponse(assignment=d["assignment"], delivery=d["delivery"])


@router.post(
    "/assignments/{assignment_id}/steps/{step_id}/launch-session",
    response_model=LaunchAssignmentStepResponse,
)
def launch_step_session(
    assignment_id: str,
    step_id: str,
    body: LaunchAssignmentStepRequest,
    svc: Annotated[CurriculumService, Depends(get_curriculum_service)],
) -> LaunchAssignmentStepResponse:
    try:
        out = svc.launch_assignment_step_session(
            assignment_id=assignment_id,
            pack_step_id=step_id,
            snapshot_id=body.snapshot_id,
            provider_name=body.provider_name,
            learner_id=body.learner_id,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    return LaunchAssignmentStepResponse(**out)


@router.post(
    "/assignments/{assignment_id}/steps/{step_id}/attach-session",
    response_model=AttachSessionAttemptResponse,
)
def attach_session(
    assignment_id: str,
    step_id: str,
    body: AttachSessionAttemptRequest,
    svc: Annotated[CurriculumService, Depends(get_curriculum_service)],
) -> AttachSessionAttemptResponse:
    try:
        out = svc.attach_session_to_assignment_step(
            assignment_id=assignment_id,
            pack_step_id=step_id,
            session_id=body.session_id,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    return AttachSessionAttemptResponse(**out)


@router.get("/assignments/{assignment_id}/report", response_model=AssignmentReportResponse)
def assignment_report(
    assignment_id: str,
    svc: Annotated[CurriculumService, Depends(get_curriculum_service)],
) -> AssignmentReportResponse:
    try:
        r = svc.generate_assignment_report(assignment_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="assignment not found") from None
    return AssignmentReportResponse(**r.model_dump())


@router.get("/learners/{learner_id}/assignments", response_model=list[AssignmentSummaryResponse])
def learner_assignments(
    learner_id: str,
    svc: Annotated[CurriculumService, Depends(get_curriculum_service)],
) -> list[AssignmentSummaryResponse]:
    rows = svc.list_learner_assignments(learner_id)
    return [
        AssignmentSummaryResponse(
            assignment_id=a.assignment_id,
            title=a.title,
            pack_id=a.pack_id,
            status=a.status,
            learner_ids=a.learner_ids,
            created_at=a.created_at,
        )
        for a in rows
    ]


@router.post("/learners/{learner_id}/curriculum-pack-from-plan", response_model=CurriculumPackDetailResponse)
def pack_from_plan(
    learner_id: str,
    body: CurriculumPackFromPlanRequest,
    svc: Annotated[CurriculumService, Depends(get_curriculum_service)],
) -> CurriculumPackDetailResponse:
    try:
        p = svc.create_curriculum_pack_from_learning_plan(
            learner_id=learner_id,
            horizon=body.horizon,
            output_pack_id=body.output_pack_id,
            display_name=body.display_name,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    return CurriculumPackDetailResponse(
        pack_id=p.pack_id,
        display_name=p.display_name,
        description=p.description,
        author_id=p.author_id,
        version=p.version,
        target_skills=p.target_skills,
        steps=[s.model_dump() for s in p.steps],
        tags=p.tags,
        metadata=p.metadata,
    )
