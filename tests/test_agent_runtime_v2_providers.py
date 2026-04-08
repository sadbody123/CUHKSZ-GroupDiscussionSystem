"""Tests for V2 provider abstraction and adapters."""

from __future__ import annotations

from app.agent_runtime_v2.providers.adapters.mock_adapter import MockChatProvider
from app.agent_runtime_v2.providers.adapters.openai_compatible_adapter import OpenAICompatibleChatProvider
from app.agent_runtime_v2.providers.models import ChatMessage, ChatRequest
from app.runtime.schemas.llm import GenerationResponse


def test_mock_adapter_capabilities_and_chat() -> None:
    provider = MockChatProvider()
    assert provider.capabilities.supports_streaming is False
    assert provider.capabilities.supports_embeddings is False
    out = provider.chat(ChatRequest(model="mock-1", messages=[ChatMessage(role="user", content="hello")]))
    assert out.provider_name == "mock"
    assert out.message.role == "assistant"
    assert out.message.content


def test_openai_compatible_adapter_exposes_capabilities_without_network() -> None:
    provider = OpenAICompatibleChatProvider()
    assert provider.name == "openai_compatible"
    assert provider.capabilities.supports_json_mode is False
    assert provider.capabilities.supports_tool_calling is False


def test_openai_compatible_adapter_maps_usage() -> None:
    class _FakeV1Provider:
        def generate(self, request):
            return GenerationResponse(
                provider_name="openai_compatible",
                model=request.model or "gpt-test",
                text="ok",
                raw={"usage": {"prompt_tokens": 3, "completion_tokens": 2, "total_tokens": 5}},
                metadata={},
            )

    provider = OpenAICompatibleChatProvider(provider=_FakeV1Provider())  # type: ignore[arg-type]
    out = provider.chat(ChatRequest(model="gpt-test", messages=[ChatMessage(role="user", content="hello")]))
    assert out.usage is not None
    assert out.usage.total_tokens == 5
