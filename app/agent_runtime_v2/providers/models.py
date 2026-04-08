"""Provider-agnostic request/response models."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


MessageRole = Literal["system", "user", "assistant", "tool"]


class ChatMessage(BaseModel):
    role: MessageRole
    content: str
    name: str | None = None
    tool_call_id: str | None = None
    metadata: dict = Field(default_factory=dict)


class UsageMetadata(BaseModel):
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    total_tokens: int | None = None
    reasoning_tokens: int | None = None
    metadata: dict = Field(default_factory=dict)


class ChatRequest(BaseModel):
    model: str | None = None
    messages: list[ChatMessage] = Field(default_factory=list)
    temperature: float | None = None
    max_tokens: int | None = None
    stream: bool = False
    response_format: dict | None = None
    metadata: dict = Field(default_factory=dict)


class ChatResponse(BaseModel):
    provider_name: str
    model: str | None = None
    message: ChatMessage
    usage: UsageMetadata | None = None
    raw: dict | None = None
    metadata: dict = Field(default_factory=dict)


class EmbeddingRequest(BaseModel):
    model: str | None = None
    inputs: list[str] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)


class EmbeddingVector(BaseModel):
    index: int
    embedding: list[float]


class EmbeddingResponse(BaseModel):
    provider_name: str
    model: str | None = None
    vectors: list[EmbeddingVector] = Field(default_factory=list)
    usage: UsageMetadata | None = None
    raw: dict | None = None
    metadata: dict = Field(default_factory=dict)
