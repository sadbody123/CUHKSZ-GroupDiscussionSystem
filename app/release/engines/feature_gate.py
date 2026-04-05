"""Feature gating from release profile."""

from __future__ import annotations

from app.release.loaders.profile_loader import load_release_profile
from app.release.schemas.profile import ReleaseProfile


def is_capability_enabled(profile: ReleaseProfile, capability_id: str) -> bool:
    if capability_id in profile.disabled_capabilities:
        return False
    if profile.metadata.get("strict_allowlist"):
        return capability_id in profile.enabled_capabilities
    if profile.enabled_capabilities:
        return capability_id in profile.enabled_capabilities
    return True


def is_experimental_visible(profile: ReleaseProfile, capability_id: str) -> bool:
    return capability_id in profile.experimental_capabilities


def load_profile_or_default(profile_id: str | None) -> ReleaseProfile:
    from app.ops.settings import get_ops_settings

    s = get_ops_settings()
    pid = profile_id or getattr(s, "active_release_profile", None) or "v1_demo"
    return load_release_profile(pid)


def ui_panel_visible(profile: ReleaseProfile, panel_key: str) -> bool:
    pol = profile.ui_visibility_policy or {}
    if panel_key in pol:
        return bool(pol[panel_key])
    return True


def api_route_visible(profile: ReleaseProfile, route_tag: str) -> bool:
    pol = profile.api_visibility_policy or {}
    if route_tag in pol:
        return bool(pol[route_tag])
    return True
