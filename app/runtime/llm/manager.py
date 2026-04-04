"""Resolve provider by name."""

from __future__ import annotations

from app.runtime.llm.base import BaseLLMProvider
from app.runtime.llm.config import load_llm_config
from app.runtime.llm.providers.mock_provider import MockProvider
from app.runtime.llm.providers.openai_compatible import OpenAICompatibleProvider


def get_provider(name: str | None) -> BaseLLMProvider:
    cfg = load_llm_config()
    n = (name or cfg.llm_provider or "mock").lower().strip()
    if n in ("mock", "", "none", "offline"):
        return MockProvider()
    if n in ("openai", "openai_compatible", "openai-compatible"):
        return OpenAICompatibleProvider()
    return MockProvider()
