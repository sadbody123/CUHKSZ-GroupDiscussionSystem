"""AssessmentTemplate schema."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class AssessmentTemplate(BaseModel):
    template_id: str
    display_name: str
    description: str | None = None
    simulated_group_size: int = 4
    prep_seconds: int | None = 60
    intro_seconds_per_side: int = 90
    discussion_seconds: int = 600
    summary_seconds_per_side: int = 60
    strict_interrupt_rules: bool = False
    no_mid_session_feedback: bool = True
    expected_user_contribution_target: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)
