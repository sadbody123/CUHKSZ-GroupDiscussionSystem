"""API endpoints for runtime V2 review workflow."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.deps import get_runtime_review_service
from app.api.schemas.runtime_review import (
    ApplyEditedDraftRequest,
    ApproveRuntimeReviewRequest,
    RejectRuntimeReviewRequest,
    ResumeRuntimeReviewRequest,
    RuntimeReviewActionResponse,
    RuntimeReviewDetailResponse,
    RuntimeReviewMetricsResponse,
    RuntimeReviewSummaryResponse,
)
from app.application.runtime_review_service import RuntimeReviewService

router = APIRouter(prefix="/runtime-reviews", tags=["runtime-reviews"])


def _to_detail(raw: dict) -> RuntimeReviewDetailResponse:
    return RuntimeReviewDetailResponse(**raw)


def _to_summary(raw: dict) -> RuntimeReviewSummaryResponse:
    return RuntimeReviewSummaryResponse(
        review_id=raw["review_id"],
        session_id=raw["session_id"],
        run_id=raw["run_id"],
        topic_id=raw.get("topic_id"),
        status=raw["status"],
        interrupt_reason=raw.get("interrupt_reason"),
        quality_flags=list(raw.get("quality_flags") or []),
        version=int(raw.get("version", 1)),
        allowed_actions=list(raw.get("allowed_actions") or []),
        updated_at=raw["updated_at"],
    )


@router.get("", response_model=list[RuntimeReviewSummaryResponse])
def list_runtime_reviews(
    svc: Annotated[RuntimeReviewService, Depends(get_runtime_review_service)],
    status: str = Query("pending"),
    session_id: str | None = Query(None),
    topic_id: str | None = Query(None),
) -> list[RuntimeReviewSummaryResponse]:
    try:
        rows = svc.list_reviews(status=status, session_id=session_id, topic_id=topic_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    return [_to_summary(r) for r in rows]


@router.get("/{review_id}", response_model=RuntimeReviewDetailResponse)
def get_runtime_review(
    review_id: str,
    svc: Annotated[RuntimeReviewService, Depends(get_runtime_review_service)],
) -> RuntimeReviewDetailResponse:
    row = svc.get_review(review_id)
    if not row:
        raise HTTPException(status_code=404, detail="review not found")
    return _to_detail(row)


@router.post("/{review_id}/approve", response_model=RuntimeReviewActionResponse)
def approve_runtime_review(
    review_id: str,
    body: ApproveRuntimeReviewRequest,
    svc: Annotated[RuntimeReviewService, Depends(get_runtime_review_service)],
) -> RuntimeReviewActionResponse:
    try:
        row = svc.approve_review(
            review_id,
            action=body.action,
            expected_version=body.expected_version,
            updated_by=body.updated_by,
            payload=body.payload,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    return RuntimeReviewActionResponse(review=_to_detail(row), result={"action": body.action})


@router.post("/{review_id}/reject", response_model=RuntimeReviewActionResponse)
def reject_runtime_review(
    review_id: str,
    body: RejectRuntimeReviewRequest,
    svc: Annotated[RuntimeReviewService, Depends(get_runtime_review_service)],
) -> RuntimeReviewActionResponse:
    try:
        row = svc.reject_review(
            review_id,
            reason=body.reason,
            expected_version=body.expected_version,
            updated_by=body.updated_by,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    return RuntimeReviewActionResponse(review=_to_detail(row), result={"action": "reject"})


@router.post("/{review_id}/resume", response_model=dict)
def resume_runtime_review(
    review_id: str,
    body: ResumeRuntimeReviewRequest,
    svc: Annotated[RuntimeReviewService, Depends(get_runtime_review_service)],
) -> dict:
    try:
        return svc.resume_from_review(review_id, additional_steps=body.additional_steps)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.post("/{review_id}/apply-edited-draft", response_model=dict)
def apply_edited_draft(
    review_id: str,
    body: ApplyEditedDraftRequest,
    svc: Annotated[RuntimeReviewService, Depends(get_runtime_review_service)],
) -> dict:
    try:
        return svc.apply_edited_draft(
            review_id,
            edited_text=body.edited_text,
            expected_version=body.expected_version,
            updated_by=body.updated_by,
            note=body.note,
            resume_after_apply=body.resume_after_apply,
            additional_steps=body.additional_steps,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get("/metrics/summary", response_model=RuntimeReviewMetricsResponse)
def runtime_review_metrics(
    svc: Annotated[RuntimeReviewService, Depends(get_runtime_review_service)],
) -> RuntimeReviewMetricsResponse:
    return RuntimeReviewMetricsResponse(**svc.get_metrics())
