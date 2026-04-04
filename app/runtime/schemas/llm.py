"""LLM request/response models."""

from __future__ import annotations

from pydantic import BaseModel, Field


class LLMMessage(BaseModel):
    role: str
    content: str


class GenerationRequest(BaseModel):
    provider_name: str
    model: str | None = None
    messages: list[LLMMessage] = Field(default_factory=list)
    temperature: float | None = None
    max_tokens: int | None = None
    metadata: dict = Field(default_factory=dict)


class GenerationResponse(BaseModel):
    provider_name: str
    model: str | None = None
    text: str
    raw: dict | None = None
    metadata: dict = Field(default_factory=dict)
