"""Runtime profile (YAML-driven configuration)."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class RuntimeProfile(BaseModel):
    """Merged runtime configuration for retrieval, orchestration, analysis, prompting."""

    profile_id: str = "default"
    description: str | None = None
    retrieval: dict[str, Any] = Field(default_factory=dict)
    orchestration: dict[str, Any] = Field(default_factory=dict)
    analyzer: dict[str, Any] = Field(default_factory=dict)
    prompting: dict[str, Any] = Field(default_factory=dict)
    coach: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)

    def merged_dict(self) -> dict[str, Any]:
        return {
            "profile_id": self.profile_id,
            "description": self.description,
            "retrieval": dict(self.retrieval),
            "orchestration": dict(self.orchestration),
            "analyzer": dict(self.analyzer),
            "prompting": dict(self.prompting),
            "coach": dict(self.coach),
            "metadata": dict(self.metadata),
        }
