"""Bridge helpers for wiring V2 runtime into existing application services."""

from __future__ import annotations

from app.agent_runtime_v2.facade.runtime_factory import create_runtime_facade
from app.application.config import AppConfig
from app.application.session_service import SessionService


def build_discussion_runtime(config: AppConfig, sessions: SessionService):
    """Return V2 runtime facade when enabled, else ``None``."""
    return create_runtime_facade(config, sessions)
