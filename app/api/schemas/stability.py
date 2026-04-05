"""API responses for stability / E2E / RC."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class E2EScenarioSummaryResponse(BaseModel):
    scenarios: list[dict[str, Any]]


class E2EScenarioDetailResponse(BaseModel):
    scenario: dict[str, Any]


class E2ERunResultResponse(BaseModel):
    result: dict[str, Any]


class ConsistencySummaryResponse(BaseModel):
    summary: dict[str, Any]


class StabilityReportResponse(BaseModel):
    report: dict[str, Any]


class KnownIssuesResponse(BaseModel):
    issues: list[dict[str, Any]]


class ReleaseCandidateReportResponse(BaseModel):
    report: dict[str, Any]


class E2EMatrixRunResponse(BaseModel):
    results: list[dict[str, Any]]
