"""Authoring API schemas."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class AuthorableArtifactSummaryResponse(BaseModel):
    artifact_ref_id: str
    artifact_type: str
    artifact_id: str
    source_type: str
    version: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class CreateDraftRequest(BaseModel):
    artifact_type: str
    artifact_id: str | None = None
    draft_id: str
    author_id: str | None = None
    as_derivative: bool = False
    title: str | None = None
    initial_content: dict[str, Any] | None = None


class DraftSummaryResponse(BaseModel):
    draft_id: str
    artifact_type: str
    artifact_id: str
    status: str
    title: str | None = None
    updated_at: str | None = None


class DraftDetailResponse(BaseModel):
    draft: dict[str, Any]


class ValidateDraftRequest(BaseModel):
    pass


class ValidationReportResponse(BaseModel):
    report: dict[str, Any]


class PreviewDraftRequest(BaseModel):
    preview_kind: str = "pack_walkthrough"
    snapshot_id: str | None = None
    provider_name: str | None = "mock"
    learner_id: str | None = None


class PreviewResultResponse(BaseModel):
    result: dict[str, Any]


class PublishDraftRequest(BaseModel):
    published_version: str


class PatchGenerateRequest(BaseModel):
    source_type: str
    source_id: str


class PatchProposalResponse(BaseModel):
    patch: dict[str, Any]


class PublicationSummaryResponse(BaseModel):
    publication_id: str
    artifact_type: str
    artifact_id: str
    published_version: str
    published_at: str


class PublicationDetailResponse(BaseModel):
    publication: dict[str, Any]
