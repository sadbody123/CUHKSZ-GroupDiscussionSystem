"""Review workspace endpoints."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.deps import get_review_service
from app.api.schemas.review import (
    CalibrationReportResponse,
    CreateReviewerRequest,
    ReviewedOutputResponse,
    ReviewerDetailResponse,
    ReviewerSummaryResponse,
    ReviewPackDetailResponse,
    ReviewPackSummaryResponse,
    SessionReviewSummaryResponse,
    SubmitReviewRequest,
    SubmitReviewResponse,
)
from app.application.review_service import ReviewService

router = APIRouter(tags=["reviews"])


@router.post("/reviewers", response_model=ReviewerDetailResponse)
def create_reviewer(
    body: CreateReviewerRequest,
    svc: Annotated[ReviewService, Depends(get_review_service)],
) -> ReviewerDetailResponse:
    try:
        p = svc.create_reviewer(
            reviewer_id=body.reviewer_id,
            display_name=body.display_name,
            role_title=body.role_title,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    return ReviewerDetailResponse(**p.model_dump())


@router.get("/reviewers", response_model=list[ReviewerSummaryResponse])
def list_reviewers(svc: Annotated[ReviewService, Depends(get_review_service)]) -> list[ReviewerSummaryResponse]:
    rows = svc.list_reviewers()
    return [ReviewerSummaryResponse(**r.model_dump()) for r in rows]


@router.get("/reviewers/{reviewer_id}", response_model=ReviewerDetailResponse)
def get_reviewer(
    reviewer_id: str,
    svc: Annotated[ReviewService, Depends(get_review_service)],
) -> ReviewerDetailResponse:
    p = svc.get_reviewer(reviewer_id)
    if not p:
        raise HTTPException(status_code=404, detail="reviewer not found")
    return ReviewerDetailResponse(**p.model_dump())


@router.post("/sessions/{session_id}/review-pack", response_model=ReviewPackDetailResponse)
def create_review_pack_for_session(
    session_id: str,
    svc: Annotated[ReviewService, Depends(get_review_service)],
) -> ReviewPackDetailResponse:
    try:
        pack = svc.create_review_pack(session_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    return ReviewPackDetailResponse(**pack.model_dump())


@router.get("/review-packs", response_model=list[ReviewPackSummaryResponse])
def list_review_packs(
    svc: Annotated[ReviewService, Depends(get_review_service)],
    session_id: str | None = Query(None),
) -> list[ReviewPackSummaryResponse]:
    packs = svc.list_review_packs()
    if session_id:
        packs = [p for p in packs if p.session_id == session_id]
    return [
        ReviewPackSummaryResponse(
            review_pack_id=p.review_pack_id,
            session_id=p.session_id,
            status=p.status,
            created_at=p.created_at,
            topic_id=p.topic_id,
            mode_id=p.mode_id,
        )
        for p in packs
    ]


@router.get("/review-packs/{review_pack_id}", response_model=ReviewPackDetailResponse)
def get_review_pack(
    review_pack_id: str,
    svc: Annotated[ReviewService, Depends(get_review_service)],
) -> ReviewPackDetailResponse:
    try:
        p = svc.get_review_pack(review_pack_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="review pack not found") from None
    return ReviewPackDetailResponse(**p.model_dump())


@router.post("/review-packs/{review_pack_id}/submit", response_model=SubmitReviewResponse)
def submit_review(
    review_pack_id: str,
    body: SubmitReviewRequest,
    svc: Annotated[ReviewService, Depends(get_review_service)],
) -> SubmitReviewResponse:
    payload = {
        "rubric_scores": body.rubric_scores,
        "annotations": body.annotations,
        "override_decisions": body.override_decisions,
        "overall_judgment": body.overall_judgment,
        "summary_notes": body.summary_notes,
        "metadata": body.metadata,
    }
    try:
        hr = svc.submit_human_review(
            review_pack_id=review_pack_id,
            reviewer_id=body.reviewer_id,
            payload=payload,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    return SubmitReviewResponse(
        review_id=hr.review_id,
        review_pack_id=hr.review_pack_id,
        reviewer_id=hr.reviewer_id,
        created_at=hr.created_at,
    )


@router.get("/sessions/{session_id}/reviews", response_model=list[dict])
def session_reviews(
    session_id: str,
    svc: Annotated[ReviewService, Depends(get_review_service)],
) -> list[dict]:
    rows = svc.get_session_reviews(session_id)
    return [r.model_dump() for r in rows]


@router.get("/sessions/{session_id}/review-summary", response_model=SessionReviewSummaryResponse)
def session_review_summary(
    session_id: str,
    svc: Annotated[ReviewService, Depends(get_review_service)],
) -> SessionReviewSummaryResponse:
    s = svc.get_review_summary(session_id)
    return SessionReviewSummaryResponse(**s)


@router.get("/sessions/{session_id}/calibration", response_model=CalibrationReportResponse | None)
def session_calibration(
    session_id: str,
    svc: Annotated[ReviewService, Depends(get_review_service)],
) -> CalibrationReportResponse | None:
    summ = svc.get_review_summary(session_id)
    cal = summ.get("latest_calibration")
    if not cal:
        return None
    return CalibrationReportResponse(**cal)
