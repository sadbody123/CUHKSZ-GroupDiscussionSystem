"""V2 chat adapter wrapping the existing V1 mock provider."""

from __future__ import annotations

from app.agent_runtime_v2.providers.capabilities import ModelCapabilities
from app.agent_runtime_v2.providers.chat import ChatProvider
from app.agent_runtime_v2.providers.models import ChatMessage, ChatRequest, ChatResponse
from app.runtime.llm.providers.mock_provider import MockProvider
from app.runtime.schemas.llm import GenerationRequest, LLMMessage


class MockChatProvider(ChatProvider):
    name = "mock"

    def __init__(self, provider: MockProvider | None = None) -> None:
        self._provider = provider or MockProvider()

    @property
    def capabilities(self) -> ModelCapabilities:
        return ModelCapabilities(
            supports_structured_output=False,
            supports_json_mode=False,
            supports_streaming=False,
            supports_tool_calling=False,
            supports_embeddings=False,
            metadata={"adapter": "v1_mock"},
        )

    def chat(self, request: ChatRequest) -> ChatResponse:
        gen = self._provider.generate(
            GenerationRequest(
                provider_name=self.name,
                model=request.model,
                messages=[LLMMessage(role=m.role, content=m.content) for m in request.messages],
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                metadata=request.metadata,
            )
        )
        return ChatResponse(
            provider_name=gen.provider_name,
            model=gen.model,
            message=ChatMessage(role="assistant", content=gen.text),
            raw=gen.raw,
            metadata=gen.metadata,
        )
