"""Environment-driven LLM settings."""

from __future__ import annotations

import os

from pydantic import BaseModel, Field


class LLMEnvConfig(BaseModel):
    llm_provider: str = Field(default_factory=lambda: os.environ.get("LLM_PROVIDER", "mock"))
    openai_api_key: str | None = Field(default_factory=lambda: os.environ.get("OPENAI_API_KEY"))
    openai_base_url: str = Field(
        default_factory=lambda: os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
    )
    openai_model: str = Field(default_factory=lambda: os.environ.get("OPENAI_MODEL", "gpt-4o-mini"))


def load_llm_config() -> LLMEnvConfig:
    return LLMEnvConfig()
