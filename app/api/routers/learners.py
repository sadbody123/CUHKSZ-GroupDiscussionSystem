"""Learner profile, timeline, recommendations, plans, reports."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.deps import get_learner_service, get_mode_service
from app.api.schemas.mode import DrillRecommendationResponse
from app.api.schemas.learner import (
    AttachSessionToLearnerRequest,
    AttachSessionToLearnerResponse,
    CreateLearnerRequest,
    LearnerProfileResponse,
    LearnerReportResponse,
    LearnerSummaryResponse,
    LearnerTimelineResponse,
    LearningPlanResponse,
    RecommendationItemResponse,
    RebuildLearnerResponse,
)
from app.application.learner_service import LearnerService
from app.application.mode_service import ModeService

router = APIRouter(prefix="/learners", tags=["learners"])


@router.post("", response_model=LearnerProfileResponse)
def create_learner(
    body: CreateLearnerRequest,
    svc: Annotated[LearnerService, Depends(get_learner_service)],
) -> LearnerProfileResponse:
    try:
        p = svc.create_learner(body.learner_id, display_name=body.display_name)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    return LearnerProfileResponse(**p.model_dump())


@router.get("", response_model=list[LearnerSummaryResponse])
def list_learners(svc: Annotated[LearnerService, Depends(get_learner_service)]) -> list[LearnerSummaryResponse]:
    rows = svc.list_learners()
    return [LearnerSummaryResponse(**r) for r in rows]


@router.get("/{learner_id}/drills", response_model=list[DrillRecommendationResponse])
def learner_drills(
    learner_id: str,
    msvc: Annotated[ModeService, Depends(get_mode_service)],
) -> list[DrillRecommendationResponse]:
    try:
        rows = msvc.generate_drills_for_learner(learner_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    return [DrillRecommendationResponse.model_validate(r) for r in rows]


@router.get("/{learner_id}", response_model=LearnerProfileResponse)
def get_learner(
    learner_id: str,
    svc: Annotated[LearnerService, Depends(get_learner_service)],
) -> LearnerProfileResponse:
    p = svc.get_learner_profile(learner_id)
    if not p:
        raise HTTPException(status_code=404, detail="learner not found")
    return LearnerProfileResponse(**p.model_dump())


@router.post("/{learner_id}/rebuild", response_model=RebuildLearnerResponse)
def rebuild_learner(
    learner_id: str,
    svc: Annotated[LearnerService, Depends(get_learner_service)],
) -> RebuildLearnerResponse:
    try:
        svc.rebuild_learner_profile(learner_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    return RebuildLearnerResponse(learner_id=learner_id)


@router.get("/{learner_id}/timeline", response_model=LearnerTimelineResponse)
def learner_timeline(
    learner_id: str,
    svc: Annotated[LearnerService, Depends(get_learner_service)],
) -> LearnerTimelineResponse:
    if not svc.get_learner_profile(learner_id):
        raise HTTPException(status_code=404, detail="learner not found")
    pts = svc.get_timeline(learner_id)
    return LearnerTimelineResponse(learner_id=learner_id, points=pts)


@router.get("/{learner_id}/recommendations", response_model=list[RecommendationItemResponse])
def learner_recommendations(
    learner_id: str,
    svc: Annotated[LearnerService, Depends(get_learner_service)],
) -> list[RecommendationItemResponse]:
    try:
        items = svc.get_recommendations(learner_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    return [RecommendationItemResponse(**x.model_dump()) for x in items]


@router.get("/{learner_id}/learning-plan", response_model=LearningPlanResponse)
def learner_learning_plan(
    learner_id: str,
    svc: Annotated[LearnerService, Depends(get_learner_service)],
    horizon: int | None = Query(None, ge=3, le=5),
) -> LearningPlanResponse:
    if not svc.get_learner_profile(learner_id):
        raise HTTPException(status_code=404, detail="learner not found")
    try:
        plan = svc.generate_learning_plan(learner_id, horizon=horizon)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    return LearningPlanResponse(**plan.model_dump())


@router.get("/{learner_id}/report", response_model=LearnerReportResponse)
def learner_report(
    learner_id: str,
    svc: Annotated[LearnerService, Depends(get_learner_service)],
) -> LearnerReportResponse:
    try:
        rep = svc.build_learner_report(learner_id, persist_report=False)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    return LearnerReportResponse(**rep)
