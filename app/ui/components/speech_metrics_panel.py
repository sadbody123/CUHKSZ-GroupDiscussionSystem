"""Speech proxy metrics — API-driven."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import streamlit as st

from app.ui.api_client import ApiError, DiscussionApiClient


def render_speech_metrics_panel(
    client: DiscussionApiClient,
    session_id: str,
    turns: list[dict[str, Any]],
    *,
    on_refresh: Callable[[], None],
    key_prefix: str = "sp_",
) -> None:
    st.subheader("Speech delivery (proxy)")
    st.caption(
        "Metrics are heuristic estimates only — not pronunciation scores. "
        "See disclaimer in API responses."
    )
    audio_turns = [t for t in turns if t.get("audio_asset_id")]
    if not audio_turns:
        st.caption("No user audio turns to analyze.")
        return
    tid = st.selectbox(
        "Turn",
        options=[t.get("turn_id") for t in audio_turns],
        format_func=lambda x: str(x),
        key=f"{key_prefix}sel",
    )
    pid = st.text_input("Profile id", value="speech_default", key=f"{key_prefix}pid")
    if st.button("Analyze speech", key=f"{key_prefix}go"):
        try:
            r = client.analyze_turn_speech(session_id, str(tid), profile_id=pid or None)
            st.json(r.get("analysis") or r)
        except ApiError as e:
            st.error(str(e))
    if st.button("Analyze full session speech", key=f"{key_prefix}sess"):
        try:
            r = client.analyze_session_speech(session_id, profile_id=pid or None)
            st.json(r.get("report") or r)
            on_refresh()
        except ApiError as e:
            st.error(str(e))
