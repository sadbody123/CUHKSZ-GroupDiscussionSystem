"""System info (non-secret)."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.deps import get_config, get_release_service
from app.api.schemas.release import (
    CapabilitySummaryResponse,
    DemoScenarioResultResponse,
    DemoScenarioRunRequest,
    ReadinessReportResponse,
    ReleaseProfileResponse,
    ReleaseVisibilityResponse,
    ScopeFreezeSummaryResponse,
)
from app.api.schemas.system import SystemInfoResponse
from app.application.config import AppConfig
from app.application.release_service import ReleaseService
from app.ops.settings import get_ops_settings
from app.ops.version import get_app_version

router = APIRouter(tags=["system"])


@router.get("/system/info", response_model=SystemInfoResponse)
def system_info(cfg: Annotated[AppConfig, Depends(get_config)]) -> SystemInfoResponse:
    o = get_ops_settings()
    return SystemInfoResponse(
        app_name=o.app_name,
        app_version=o.app_version or get_app_version(),
        app_env=o.app_env,
        snapshot_root=str(cfg.snapshot_root.resolve()),
        default_provider=cfg.default_provider,
        default_runtime_profile=cfg.default_runtime_profile,
        bundle_dir=str(o.bundle_dir.resolve()),
        feature_flags={
            "structured_logging": o.structured_logging,
            "active_release_profile": getattr(o, "active_release_profile", "v1_demo"),
        },
    )


@router.get("/system/capabilities", response_model=CapabilitySummaryResponse)
def system_capabilities(svc: Annotated[ReleaseService, Depends(get_release_service)]) -> CapabilitySummaryResponse:
    return CapabilitySummaryResponse(capabilities=svc.list_capabilities())


@router.get("/system/release-profile", response_model=ReleaseProfileResponse)
def active_release_profile(
    svc: Annotated[ReleaseService, Depends(get_release_service)],
    profile_id: str | None = Query(None),
) -> ReleaseProfileResponse:
    try:
        return ReleaseProfileResponse(profile=svc.get_release_profile(profile_id))
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="release profile not found") from None


@router.get("/system/release-profiles", response_model=list[str])
def list_release_profiles(svc: Annotated[ReleaseService, Depends(get_release_service)]) -> list[str]:
    return svc.list_release_profiles()


@router.get("/system/readiness", response_model=ReadinessReportResponse)
def system_readiness(
    svc: Annotated[ReleaseService, Depends(get_release_service)],
    profile_id: str | None = Query(None),
) -> ReadinessReportResponse:
    rep = svc.run_readiness_audit(profile_id)
    return ReadinessReportResponse(report=rep.model_dump())


@router.post("/system/demo-scenarios/{scenario_id}/run", response_model=DemoScenarioResultResponse)
def run_demo_scenario_ep(
    scenario_id: str,
    body: DemoScenarioRunRequest,
    svc: Annotated[ReleaseService, Depends(get_release_service)],
) -> DemoScenarioResultResponse:
    try:
        r = svc.run_demo_scenario(
            scenario_id,
            profile_id=body.profile_id,
            snapshot_id=body.snapshot_id,
            topic_id=body.topic_id,
            provider_name=body.provider_name,
        )
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="scenario or profile not found") from None
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    return DemoScenarioResultResponse(result=r.model_dump())


@router.get("/system/scope-freeze", response_model=ScopeFreezeSummaryResponse)
def scope_freeze(
    svc: Annotated[ReleaseService, Depends(get_release_service)],
    profile_id: str | None = Query(None),
) -> ScopeFreezeSummaryResponse:
    return ScopeFreezeSummaryResponse(summary=svc.get_scope_freeze_summary(profile_id))


@router.get("/system/release-visibility", response_model=ReleaseVisibilityResponse)
def release_visibility(
    svc: Annotated[ReleaseService, Depends(get_release_service)],
    profile_id: str | None = Query(None),
) -> ReleaseVisibilityResponse:
    return ReleaseVisibilityResponse(state=svc.get_release_visibility_state(profile_id))
