"""Authoring workspace API."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.deps import get_authoring_service
from app.api.schemas.authoring import (
    AuthorableArtifactSummaryResponse,
    CreateDraftRequest,
    DraftDetailResponse,
    DraftSummaryResponse,
    PatchGenerateRequest,
    PatchProposalResponse,
    PreviewDraftRequest,
    PreviewResultResponse,
    PublicationDetailResponse,
    PublicationSummaryResponse,
    PublishDraftRequest,
    ValidationReportResponse,
)
from app.application.authoring_service import AuthoringService

router = APIRouter(prefix="/authoring", tags=["authoring"])


@router.get("/artifacts", response_model=list[AuthorableArtifactSummaryResponse])
def list_artifacts(
    svc: Annotated[AuthoringService, Depends(get_authoring_service)],
    artifact_type: str | None = Query(None),
    source_type: str | None = Query(None),
) -> list[AuthorableArtifactSummaryResponse]:
    try:
        rows = svc.list_authorable_artifacts(artifact_type=artifact_type, source_type=source_type)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    return [AuthorableArtifactSummaryResponse(**r.model_dump()) for r in rows]


@router.post("/drafts", response_model=DraftDetailResponse)
def create_draft(body: CreateDraftRequest, svc: Annotated[AuthoringService, Depends(get_authoring_service)]) -> DraftDetailResponse:
    try:
        d = svc.create_draft(
            draft_id=body.draft_id,
            artifact_type=body.artifact_type,
            artifact_id=body.artifact_id,
            author_id=body.author_id,
            as_derivative=body.as_derivative,
            initial_content=body.initial_content,
            title=body.title,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    return DraftDetailResponse(draft=d.model_dump())


@router.get("/drafts", response_model=list[DraftSummaryResponse])
def list_drafts(svc: Annotated[AuthoringService, Depends(get_authoring_service)]) -> list[DraftSummaryResponse]:
    rows = svc.list_drafts()
    return [
        DraftSummaryResponse(
            draft_id=d.draft_id,
            artifact_type=d.artifact_type,
            artifact_id=d.artifact_id,
            status=d.status,
            title=d.title,
            updated_at=d.updated_at,
        )
        for d in rows
    ]


@router.get("/drafts/{draft_id}", response_model=DraftDetailResponse)
def get_draft(draft_id: str, svc: Annotated[AuthoringService, Depends(get_authoring_service)]) -> DraftDetailResponse:
    try:
        d = svc.get_draft(draft_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="draft not found") from None
    return DraftDetailResponse(draft=d.model_dump())


@router.post("/drafts/{draft_id}/validate", response_model=ValidationReportResponse)
def validate_draft(draft_id: str, svc: Annotated[AuthoringService, Depends(get_authoring_service)]) -> ValidationReportResponse:
    try:
        rep = svc.validate_draft(draft_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="draft not found") from None
    return ValidationReportResponse(report=rep.model_dump())


@router.post("/drafts/{draft_id}/preview", response_model=PreviewResultResponse)
def preview_draft(
    draft_id: str,
    body: PreviewDraftRequest,
    svc: Annotated[AuthoringService, Depends(get_authoring_service)],
) -> PreviewResultResponse:
    try:
        res = svc.preview_draft(
            draft_id,
            preview_kind=body.preview_kind,
            snapshot_id=body.snapshot_id,
            provider_name=body.provider_name,
            learner_id=body.learner_id,
        )
    except ValueError as e:
        msg = str(e)
        code = 404 if "not found" in msg else 400
        raise HTTPException(status_code=code, detail=msg) from e
    return PreviewResultResponse(result=res.model_dump())


@router.post("/drafts/{draft_id}/publish", response_model=PublicationDetailResponse)
def publish_draft_ep(
    draft_id: str,
    body: PublishDraftRequest,
    svc: Annotated[AuthoringService, Depends(get_authoring_service)],
) -> PublicationDetailResponse:
    try:
        rec = svc.publish_draft(draft_id, published_version=body.published_version)
    except ValueError as e:
        msg = str(e)
        code = 404 if "not found" in msg else 400
        raise HTTPException(status_code=code, detail=msg) from e
    return PublicationDetailResponse(publication=rec.model_dump())


@router.get("/patches", response_model=list[PatchProposalResponse])
def list_patches(svc: Annotated[AuthoringService, Depends(get_authoring_service)]) -> list[PatchProposalResponse]:
    rows = svc.list_patch_proposals()
    return [PatchProposalResponse(patch=p.model_dump()) for p in rows]


@router.post("/patches/generate", response_model=list[PatchProposalResponse])
def generate_patches(
    body: PatchGenerateRequest,
    svc: Annotated[AuthoringService, Depends(get_authoring_service)],
) -> list[PatchProposalResponse]:
    try:
        rows = svc.generate_patch_proposals(source_type=body.source_type, source_id=body.source_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    return [PatchProposalResponse(patch=p.model_dump()) for p in rows]


@router.post("/drafts/{draft_id}/apply-patch/{patch_id}", response_model=DraftDetailResponse)
def apply_patch(
    draft_id: str,
    patch_id: str,
    svc: Annotated[AuthoringService, Depends(get_authoring_service)],
) -> DraftDetailResponse:
    try:
        d = svc.apply_patch_to_draft(draft_id, patch_id)
    except ValueError as e:
        msg = str(e)
        code = 404 if "not found" in msg else 400
        raise HTTPException(status_code=code, detail=msg) from e
    return DraftDetailResponse(draft=d.model_dump())


@router.get("/publications", response_model=list[PublicationSummaryResponse])
def list_publications(
    svc: Annotated[AuthoringService, Depends(get_authoring_service)],
    artifact_type: str | None = Query(None),
) -> list[PublicationSummaryResponse]:
    rows = svc.list_publications(artifact_type=artifact_type)
    return [
        PublicationSummaryResponse(
            publication_id=r.publication_id,
            artifact_type=r.artifact_type,
            artifact_id=r.artifact_id,
            published_version=r.published_version,
            published_at=r.published_at,
        )
        for r in rows
    ]


@router.get("/publications/{publication_id}", response_model=PublicationDetailResponse)
def get_publication(publication_id: str, svc: Annotated[AuthoringService, Depends(get_authoring_service)]) -> PublicationDetailResponse:
    try:
        r = svc.get_publication(publication_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="publication not found") from None
    return PublicationDetailResponse(publication=r.model_dump())
