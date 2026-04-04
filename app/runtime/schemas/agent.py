"""Agent outputs and rendered prompts."""

from __future__ import annotations

from pydantic import BaseModel, Field


class RenderedPrompt(BaseModel):
    role: str
    template_id: str
    system_prompt: str | None = None
    user_prompt: str
    metadata: dict = Field(default_factory=dict)


class AgentReply(BaseModel):
    role: str
    text: str
    rendered_prompt_id: str | None = None
    used_pedagogy_item_ids: list[str] = Field(default_factory=list)
    used_evidence_ids: list[str] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)
