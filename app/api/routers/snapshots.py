"""Snapshot listing."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.deps import get_snapshot_service
from app.api.schemas.index import IndexStatusResponse
from app.api.schemas.snapshot import SnapshotDetailResponse, SnapshotSummaryResponse
from app.application.snapshot_service import SnapshotService

router = APIRouter(prefix="/snapshots", tags=["snapshots"])


@router.get("", response_model=list[SnapshotSummaryResponse])
def list_snapshots(svc: Annotated[SnapshotService, Depends(get_snapshot_service)]) -> list[SnapshotSummaryResponse]:
    items = svc.list_snapshots()
    return [
        SnapshotSummaryResponse(
            snapshot_id=i.snapshot_id,
            schema_version=i.schema_version,
            created_at=i.created_at,
            topic_card_count=i.topic_card_count,
            evidence_index_count=i.evidence_index_count,
            pedagogy_item_count=i.pedagogy_item_count,
            available=i.available,
        )
        for i in items
    ]


@router.get("/{snapshot_id}/index-status", response_model=IndexStatusResponse)
def get_index_status(
    snapshot_id: str,
    svc: Annotated[SnapshotService, Depends(get_snapshot_service)],
) -> IndexStatusResponse:
    data = svc.get_index_status(snapshot_id)
    return IndexStatusResponse(**data)


@router.get("/{snapshot_id}", response_model=SnapshotDetailResponse)
def get_snapshot(
    snapshot_id: str,
    svc: Annotated[SnapshotService, Depends(get_snapshot_service)],
) -> SnapshotDetailResponse:
    data = svc.get_snapshot_bundle_summary(snapshot_id)
    return SnapshotDetailResponse(
        snapshot_id=data["snapshot_id"],
        manifest=data["manifest"],
        build_report=data["build_report"],
        counts=data["counts"],
        validation_ok=bool(data["validation_ok"]),
    )
