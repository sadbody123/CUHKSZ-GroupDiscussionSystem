"""Runtime profile helper."""

from __future__ import annotations

from app.runtime.profile_resolver import resolve_runtime_profile
from app.runtime.schemas.profile import RuntimeProfile


def get_runtime_profile(profile_id: str | None) -> RuntimeProfile:
    return resolve_runtime_profile(profile_id)
