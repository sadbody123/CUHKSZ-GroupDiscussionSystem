"""Sidebar system / health summary from API."""

from __future__ import annotations

from typing import Any

import streamlit as st

from app.ui.api_client import ApiError, DiscussionApiClient


def render_system_info_panel(client: DiscussionApiClient) -> None:
    """Fetch ``/health`` and ``/system/info``; show friendly errors if unavailable."""
    st.subheader("System")
    health: dict[str, Any] | None = None
    info: dict[str, Any] | None = None
    try:
        health = client.get_health()
    except ApiError as e:
        st.warning(f"Health endpoint unavailable: {e}")
    try:
        info = client.get_system_info()
    except ApiError as e:
        st.warning(f"System info unavailable: {e}")
    if health:
        st.caption(
            f"app {health.get('app_version') or health.get('version', '?')} · "
            f"env {health.get('app_env', '?')} · "
            f"profile {health.get('default_runtime_profile', '?')}"
        )
    if info:
        st.json(
            {
                "app_name": info.get("app_name"),
                "app_version": info.get("app_version"),
                "app_env": info.get("app_env"),
                "default_provider": info.get("default_provider"),
                "default_runtime_profile": info.get("default_runtime_profile"),
                "snapshot_root": info.get("snapshot_root"),
                "bundle_dir": info.get("bundle_dir"),
                "feature_flags": info.get("feature_flags"),
            }
        )
