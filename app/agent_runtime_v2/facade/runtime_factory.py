"""Runtime backend selector for V1/V2 coexistence."""

from __future__ import annotations

from app.agent_runtime_v2.facade.discussion_runtime import AgentRuntimeFacade
from app.application.config import AppConfig
from app.application.session_service import SessionService


def resolve_runtime_backend(config: AppConfig) -> str:
    backend = str(getattr(config, "agent_runtime_backend", "v1") or "v1").strip().lower()
    return backend if backend in {"v1", "v2"} else "v1"


def create_runtime_facade(
    config: AppConfig,
    sessions: SessionService,
) -> AgentRuntimeFacade | None:
    if resolve_runtime_backend(config) != "v2":
        return None
    return AgentRuntimeFacade(config, sessions)
