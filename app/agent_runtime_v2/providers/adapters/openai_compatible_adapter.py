"""V2 chat adapter wrapping existing openai-compatible provider."""

from __future__ import annotations

from app.agent_runtime_v2.providers.capabilities import ModelCapabilities
from app.agent_runtime_v2.providers.chat import ChatProvider
from app.agent_runtime_v2.providers.models import ChatMessage, ChatRequest, ChatResponse, UsageMetadata
from app.runtime.llm.providers.openai_compatible import OpenAICompatibleProvider
from app.runtime.schemas.llm import GenerationRequest, LLMMessage


class OpenAICompatibleChatProvider(ChatProvider):
    name = "openai_compatible"

    def __init__(self, provider: OpenAICompatibleProvider | None = None) -> None:
        self._provider = provider or OpenAICompatibleProvider()

    @property
    def capabilities(self) -> ModelCapabilities:
        return ModelCapabilities(
            supports_streaming=False,
            supports_tool_calling=False,
            supports_structured_output=False,
            supports_json_mode=False,
            supports_multimodal_input=False,
            supports_reasoning_tokens=False,
            supports_embeddings=False,
            metadata={"adapter": "v1_openai_compatible"},
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
        usage = None
        if gen.raw and isinstance(gen.raw, dict):
            raw_usage = gen.raw.get("usage")
            if isinstance(raw_usage, dict):
                usage = UsageMetadata(
                    prompt_tokens=raw_usage.get("prompt_tokens"),
                    completion_tokens=raw_usage.get("completion_tokens"),
                    total_tokens=raw_usage.get("total_tokens"),
                    metadata={},
                )
        return ChatResponse(
            provider_name=gen.provider_name,
            model=gen.model,
            message=ChatMessage(role="assistant", content=gen.text),
            usage=usage,
            raw=gen.raw,
            metadata=gen.metadata,
        )
