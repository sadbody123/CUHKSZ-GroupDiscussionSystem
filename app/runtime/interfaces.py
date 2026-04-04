"""Abstract interfaces for future session / retrieval runtime (not implemented)."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Protocol


class SnapshotReader(Protocol):
    """Load normalized docs and chunks from a snapshot directory."""

    def load_manifest(self) -> Any: ...


class PracticeRuntime(ABC):
    """Future: orchestrate roles, prompts, and evidence (offline-first)."""

    @abstractmethod
    def health(self) -> dict[str, str]:
        raise NotImplementedError
