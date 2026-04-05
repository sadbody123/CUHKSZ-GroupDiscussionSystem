"""Final delivery / handover endpoints."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.deps import get_handover_service
from app.application.handover_service import HandoverService
from app.api.schemas.handover import (
    AcceptanceEvidenceResponse,
    BillOfMaterialsResponse,
    DemoKitResponse,
    DeliveryVerificationResponse,
    FinalReleaseSummaryResponse,
    HandoverKitResponse,
    ReleaseManifestResponse,
)

router = APIRouter(tags=["handover"])


def _strip_paths(d: dict) -> dict:
    return {k: v for k, v in d.items() if k not in ("path", "json_path", "output_dir", "zip_path")}


@router.get("/system/release-manifest", response_model=ReleaseManifestResponse)
def get_release_manifest(
    svc: Annotated[HandoverService, Depends(get_handover_service)],
    profile_id: str | None = Query(None),
) -> ReleaseManifestResponse:
    try:
        raw = svc.build_release_manifest(profile_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="release manifest could not be built") from None
    return ReleaseManifestResponse(manifest=raw.get("manifest") or {})


@router.get("/system/bom", response_model=BillOfMaterialsResponse)
def get_bom(
    svc: Annotated[HandoverService, Depends(get_handover_service)],
    profile_id: str | None = Query(None),
) -> BillOfMaterialsResponse:
    raw = svc.build_bom(profile_id)
    bom = raw.get("bom") or {}
    entries = bom.get("entries") or []
    warnings = bom.get("warnings") or []
    return BillOfMaterialsResponse(bom=_strip_paths(bom), entry_count=len(entries), warning_count=len(warnings))


@router.get("/system/demo-kit", response_model=DemoKitResponse)
def get_demo_kit_summary(
    svc: Annotated[HandoverService, Depends(get_handover_service)],
    profile_id: str | None = Query(None),
) -> DemoKitResponse:
    raw = svc.get_demo_kit_manifest_public(profile_id)
    if not raw:
        raise HTTPException(status_code=404, detail="demo kit not built yet")
    return DemoKitResponse(
        demo_kit_id=raw.get("demo_kit_id"),
        target_profile_id=raw.get("target_profile_id"),
        demo_scenario_ids=list(raw.get("demo_scenario_ids") or []),
        notes=list(raw.get("notes") or []),
    )


@router.get("/system/acceptance", response_model=AcceptanceEvidenceResponse)
def get_acceptance(
    svc: Annotated[HandoverService, Depends(get_handover_service)],
    profile_id: str | None = Query(None),
) -> AcceptanceEvidenceResponse:
    ev = svc.build_acceptance_evidence(profile_id)["evidence"]
    return AcceptanceEvidenceResponse(evidence=ev)


@router.post("/system/verify-delivery", response_model=DeliveryVerificationResponse)
def post_verify_delivery(
    svc: Annotated[HandoverService, Depends(get_handover_service)],
    profile_id: str | None = Query(None),
) -> DeliveryVerificationResponse:
    return DeliveryVerificationResponse(report=svc.verify_delivery(profile_id))


@router.get("/system/handover-kit", response_model=HandoverKitResponse)
def get_handover_kit(
    svc: Annotated[HandoverService, Depends(get_handover_service)],
    profile_id: str | None = Query(None),
) -> HandoverKitResponse:
    raw = svc.get_handover_kit_manifest_public(profile_id)
    if not raw:
        raise HTTPException(status_code=404, detail="handover kit not built yet")
    return HandoverKitResponse(
        handover_kit_id=raw.get("handover_kit_id"),
        notes=list(raw.get("notes") or []),
        target_audience=raw.get("target_audience"),
    )


@router.get("/system/final-release-summary", response_model=FinalReleaseSummaryResponse)
def final_release_summary(
    svc: Annotated[HandoverService, Depends(get_handover_service)],
    profile_id: str | None = Query(None),
) -> FinalReleaseSummaryResponse:
    return FinalReleaseSummaryResponse(summary=svc.get_handover_summary(profile_id))
