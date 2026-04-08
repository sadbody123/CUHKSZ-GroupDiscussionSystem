"""Provider selection tool for V2 abstractions."""

from __future__ import annotations

from app.agent_runtime_v2.providers.chat import ChatProvider
from app.agent_runtime_v2.providers.adapters.mock_adapter import MockChatProvider
from app.agent_runtime_v2.providers.adapters.openai_compatible_adapter import OpenAICompatibleChatProvider
from app.agent_runtime_v2.providers.base import ProviderError


def resolve_chat_provider(provider_name: str | None) -> ChatProvider:
    n = str(provider_name or "mock").strip().lower()
    if n in ("mock", "", "none", "offline"):
        return MockChatProvider()
    if n in ("openai", "openai_compatible", "openai-compatible"):
        return OpenAICompatibleChatProvider()
    raise ProviderError(f"Unsupported V2 chat provider: {provider_name}")
