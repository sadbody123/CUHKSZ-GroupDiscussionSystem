"""Demo scenario schemas."""

from __future__ import annotations

from pydantic import BaseModel, Field


class DemoScenario(BaseModel):
    scenario_id: str
    display_name: str
    description: str | None = None
    scenario_type: str
    required_capabilities: list[str] = Field(default_factory=list)
    required_inputs: dict = Field(default_factory=dict)
    steps: list[dict] = Field(default_factory=list)
    success_criteria: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)


class DemoScenarioResult(BaseModel):
    result_id: str
    scenario_id: str
    profile_id: str
    created_at: str
    success: bool
    step_results: list[dict] = Field(default_factory=list)
    outputs: dict = Field(default_factory=dict)
    warnings: list[str] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)
