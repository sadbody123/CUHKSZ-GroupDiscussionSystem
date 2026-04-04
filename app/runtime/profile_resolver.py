"""Merge runtime profiles with defaults (deep merge for dict sections)."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from app.runtime.profile_loader import load_profile_yaml, list_profile_ids
from app.runtime.schemas.profile import RuntimeProfile

_MERGE_KEYS = ("retrieval", "orchestration", "analyzer", "prompting", "coach", "metadata")


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    out = deepcopy(base)
    for k, v in override.items():
        if k in _MERGE_KEYS and isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = _deep_merge(out[k], v)
        else:
            out[k] = deepcopy(v)
    return out


def resolve_runtime_profile(profile_id: str | None) -> RuntimeProfile:
    """
    Resolve profile: load ``default`` as base, then merge ``profile_id`` (if not default).
    Unknown profile_id falls back to default-only merge.
    """
    pid = (profile_id or "default").strip() or "default"
    base_raw = load_profile_yaml("default")
    if pid == "default":
        return RuntimeProfile.model_validate(base_raw)
    try:
        over = load_profile_yaml(pid)
    except FileNotFoundError:
        return RuntimeProfile.model_validate(base_raw)
    merged = _deep_merge(base_raw, over)
    merged["profile_id"] = over.get("profile_id", pid)
    return RuntimeProfile.model_validate(merged)


def list_resolved_profile_summaries() -> list[dict[str, Any]]:
    """List available profile ids with descriptions from resolved profiles."""
    out: list[dict[str, Any]] = []
    for pid in list_profile_ids():
        p = resolve_runtime_profile(pid)
        out.append({"profile_id": p.profile_id, "description": p.description})
    return out
