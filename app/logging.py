"""Logging setup — delegates to ``app.ops.logging_config`` for trace-aware formatting."""

from __future__ import annotations

from app.ops.logging_config import configure_logging
from app.ops.settings import get_ops_settings


def setup_logging(level: str | None = None) -> None:
    s = get_ops_settings()
    configure_logging(level=level or s.log_level, structured=s.structured_logging)
