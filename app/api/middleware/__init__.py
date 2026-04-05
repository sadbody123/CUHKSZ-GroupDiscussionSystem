"""FastAPI middleware."""

from __future__ import annotations

from app.api.middleware.request_context import RequestContextMiddleware

__all__ = ["RequestContextMiddleware"]
