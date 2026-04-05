"""List and play session audio assets via API."""

from __future__ import annotations

import streamlit as st

from app.ui.api_client import ApiError, DiscussionApiClient


def render_audio_player_panel(client: DiscussionApiClient, session_id: str, *, key_prefix: str = "ap_") -> None:
    st.subheader("Session audio")
    try:
        data = client.list_session_audio_assets(session_id)
    except ApiError as e:
        st.caption(f"Could not list audio: {e}")
        return
    assets = data.get("assets") or []
    if not assets:
        st.caption("No audio assets yet.")
        return
    for a in assets:
        aid = str(a.get("asset_id", ""))
        kind = str(a.get("asset_kind", ""))
        st.caption(f"{kind} — {aid[:8]}…")
        try:
            blob, mime = client.fetch_audio_bytes(aid)
            st.audio(blob, format=mime.split("/")[-1] if "/" in mime else "wav")
        except ApiError:
            st.caption("Playback failed.")
