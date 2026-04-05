"""Curriculum pack schemas."""

from __future__ import annotations

from pydantic import BaseModel, Field


class CurriculumPackStep(BaseModel):
    step_id: str
    order: int
    title: str
    objective: str = ""
    step_type: str = "topic_practice"
    topic_id: str | None = None
    drill_id: str | None = None
    mode_id: str | None = None
    preset_id: str | None = None
    runtime_profile_id: str | None = None
    assessment_template_id: str | None = None
    roster_template_id: str | None = None
    learner_mode: str | None = None
    focus_skills: list[str] = Field(default_factory=list)
    required_pedagogy_item_ids: list[str] = Field(default_factory=list)
    success_criteria: list[str] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)


class CurriculumPack(BaseModel):
    pack_id: str
    display_name: str
    description: str | None = None
    author_id: str | None = None
    version: str | None = "1"
    created_at: str = ""
    updated_at: str | None = None
    target_skills: list[str] = Field(default_factory=list)
    recommended_learner_levels: list[str] = Field(default_factory=list)
    steps: list[CurriculumPackStep] = Field(default_factory=list)
    linked_topic_ids: list[str] = Field(default_factory=list)
    linked_pedagogy_item_ids: list[str] = Field(default_factory=list)
    linked_drill_ids: list[str] = Field(default_factory=list)
    linked_mode_ids: list[str] = Field(default_factory=list)
    linked_assessment_template_ids: list[str] = Field(default_factory=list)
    linked_roster_template_ids: list[str] = Field(default_factory=list)
    linked_reviewed_artifact_refs: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)
