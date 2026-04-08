"""Core provider interfaces for runtime V2."""

from __future__ import annotations

from abc import ABC, abstractmethod

from app.agent_runtime_v2.providers.capabilities import ModelCapabilities


class ProviderError(RuntimeError):
    """Provider-level execution or compatibility error."""


class ProviderBase(ABC):
    name: str = "provider_base"

    @property
    @abstractmethod
    def capabilities(self) -> ModelCapabilities:
        raise NotImplementedError
