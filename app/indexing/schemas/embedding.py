"""Embedding request/response schemas."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class EmbeddingRequest(BaseModel):
    texts: list[str]
    embedder_name: str = "hash"
    model_name: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class EmbeddingResponse(BaseModel):
    embedder_name: str
    model_name: str | None = None
    vectors: list[list[float]]
    dimension: int
    metadata: dict[str, Any] = Field(default_factory=dict)
