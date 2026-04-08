"""Adapters that wrap V1 providers into V2 interfaces."""

from app.agent_runtime_v2.providers.adapters.mock_adapter import MockChatProvider
from app.agent_runtime_v2.providers.adapters.openai_compatible_adapter import OpenAICompatibleChatProvider

__all__ = ["MockChatProvider", "OpenAICompatibleChatProvider"]
