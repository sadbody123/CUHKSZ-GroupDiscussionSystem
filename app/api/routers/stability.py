"""Stability / E2E / RC endpoints under /system/..."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.deps import get_stability_service
from app.api.schemas.stability import (
    ConsistencySummaryResponse,
    E2ERunResultResponse,
    E2EScenarioDetailResponse,
    E2EScenarioSummaryResponse,
    KnownIssuesResponse,
    ReleaseCandidateReportResponse,
    StabilityReportResponse,
)
from app.application.stability_service import StabilityService

router = APIRouter(tags=["stability"])


@router.get("/system/e2e-scenarios", response_model=E2EScenarioSummaryResponse)
def list_e2e(svc: Annotated[StabilityService, Depends(get_stability_service)]) -> E2EScenarioSummaryResponse:
    return E2EScenarioSummaryResponse(scenarios=svc.list_e2e_scenarios())


@router.get("/system/e2e-scenarios/{scenario_id}", response_model=E2EScenarioDetailResponse)
def get_e2e(
    scenario_id: str,
    svc: Annotated[StabilityService, Depends(get_stability_service)],
) -> E2EScenarioDetailResponse:
    spec = svc.get_e2e_scenario(scenario_id)
    if not spec:
        raise HTTPException(status_code=404, detail="e2e scenario not found")
    return E2EScenarioDetailResponse(scenario=spec)


@router.post("/system/e2e-scenarios/{scenario_id}/run", response_model=E2ERunResultResponse)
def run_e2e(
    scenario_id: str,
    svc: Annotated[StabilityService, Depends(get_stability_service)],
    profile_id: str | None = Query(None),
    snapshot_id: str = Query("dev_snapshot_v2"),
    topic_id: str = Query("tc-campus-ai"),
    provider_name: str = Query("mock"),
) -> E2ERunResultResponse:
    r = svc.run_e2e_scenario(
        scenario_id,
        profile_id=profile_id,
        snapshot_id=snapshot_id,
        topic_id=topic_id,
        provider_name=provider_name,
    )
    return E2ERunResultResponse(result=r.model_dump())


@router.get("/system/consistency", response_model=ConsistencySummaryResponse)
def consistency_summary(
    svc: Annotated[StabilityService, Depends(get_stability_service)],
    profile_id: str | None = Query(None),
) -> ConsistencySummaryResponse:
    row = svc.run_consistency_audit(profile_id)
    return ConsistencySummaryResponse(summary=row)


@router.get("/system/stability", response_model=StabilityReportResponse)
def stability_report_ep(
    svc: Annotated[StabilityService, Depends(get_stability_service)],
    profile_id: str | None = Query(None),
    include_e2e: bool = Query(False),
    snapshot_id: str = Query("dev_snapshot_v2"),
    topic_id: str = Query("tc-campus-ai"),
) -> StabilityReportResponse:
    rep = svc.get_stability_report(profile_id, include_e2e=include_e2e, snapshot_id=snapshot_id, topic_id=topic_id)
    return StabilityReportResponse(report=rep)


@router.get("/system/known-issues", response_model=KnownIssuesResponse)
def known_issues_ep(svc: Annotated[StabilityService, Depends(get_stability_service)]) -> KnownIssuesResponse:
    return KnownIssuesResponse(issues=svc.list_known_issues())


@router.get("/system/release-candidate", response_model=ReleaseCandidateReportResponse)
def release_candidate_ep(
    svc: Annotated[StabilityService, Depends(get_stability_service)],
    profile_id: str | None = Query(None),
) -> ReleaseCandidateReportResponse:
    return ReleaseCandidateReportResponse(report=svc.build_rc_report(profile_id))
