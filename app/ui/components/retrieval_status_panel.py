"""Retrieval / index status from API (read-only)."""

from __future__ import annotations

from typing import Any

import streamlit as st

from app.ui.api_client import ApiError, DiscussionApiClient


def render_retrieval_status_panel(
    client: DiscussionApiClient,
    *,
    snapshot_id: str | None,
    session_status: dict[str, Any] | None,
) -> None:
    st.subheader("Retrieval")
    if session_status:
        st.caption(f"Profile: {session_status.get('runtime_profile_id', '?')}")
        st.caption(f"Retrieval mode: {session_status.get('retrieval_mode', '?')}")
        st.caption(f"Has indexes (session snapshot): {session_status.get('has_indexes', False)}")
    if not snapshot_id:
        st.caption("No snapshot selected.")
        return
    try:
        idx = client.get_index_status(snapshot_id)
        st.caption(f"Index on snapshot: embedder={idx.get('embedder_name')!s} dim={idx.get('dimension')!s}")
        st.caption(f"stores={idx.get('stores')} modes={idx.get('available_modes')}")
    except ApiError as e:
        st.warning(f"Index status unavailable: {e}")
