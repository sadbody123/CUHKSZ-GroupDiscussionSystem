"""E2E scenario specs and results."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class E2EScenarioSpec(BaseModel):
    model_config = ConfigDict(extra="ignore")

    scenario_id: str
    display_name: str = ""
    scenario_type: str = "text_core"
    interface_mode: str = "service"
    required_capabilities: list[str] = Field(default_factory=list)
    setup: dict = Field(default_factory=dict)
    steps: list[dict] = Field(default_factory=list)
    success_criteria: list[str] = Field(default_factory=list)
    expected_artifact_kinds: list[str] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)
    release_demo_alias: str | None = None


class E2ERunResult(BaseModel):
    run_id: str
    scenario_id: str
    profile_id: str | None = None
    interface_mode: str = "service"
    started_at: str
    ended_at: str | None = None
    success: bool
    step_results: list[dict] = Field(default_factory=list)
    produced_artifacts: dict = Field(default_factory=dict)
    warnings: list[str] = Field(default_factory=list)
    issue_ids: list[str] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)
