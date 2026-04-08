"""Provider capability flags for multi-vendor model support."""

from __future__ import annotations

from pydantic import BaseModel, Field


class ModelCapabilities(BaseModel):
    """Feature map used by runtime routing and guardrails."""

    supports_streaming: bool = False
    supports_tool_calling: bool = False
    supports_structured_output: bool = False
    supports_json_mode: bool = False
    supports_multimodal_input: bool = False
    supports_reasoning_tokens: bool = False
    supports_embeddings: bool = False
    max_input_tokens: int | None = None
    max_output_tokens: int | None = None
    metadata: dict = Field(default_factory=dict)
