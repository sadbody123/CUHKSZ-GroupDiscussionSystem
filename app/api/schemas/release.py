"""Release / system readiness API schemas."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class CapabilitySummaryResponse(BaseModel):
    capabilities: list[dict[str, Any]]


class ReleaseProfileResponse(BaseModel):
    profile: dict[str, Any]


class ReadinessReportResponse(BaseModel):
    report: dict[str, Any]


class DemoScenarioRunRequest(BaseModel):
    profile_id: str | None = None
    snapshot_id: str = "dev_snapshot_v2"
    topic_id: str = "tc-campus-ai"
    provider_name: str = "mock"


class DemoScenarioResultResponse(BaseModel):
    result: dict[str, Any]


class ScopeFreezeSummaryResponse(BaseModel):
    summary: dict[str, Any]


class ReleaseVisibilityResponse(BaseModel):
    state: dict[str, Any]
