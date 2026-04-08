"""Chat provider abstraction."""

from __future__ import annotations

from abc import abstractmethod

from app.agent_runtime_v2.providers.base import ProviderBase
from app.agent_runtime_v2.providers.models import ChatRequest, ChatResponse


class ChatProvider(ProviderBase):
    @abstractmethod
    def chat(self, request: ChatRequest) -> ChatResponse:
        raise NotImplementedError
