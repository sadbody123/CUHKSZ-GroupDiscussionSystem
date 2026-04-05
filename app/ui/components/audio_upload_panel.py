"""Upload WAV, preview ASR, optionally submit as user turn."""

from __future__ import annotations

from collections.abc import Callable

import streamlit as st

from app.ui.api_client import ApiError, DiscussionApiClient


def render_audio_upload_panel(
    client: DiscussionApiClient,
    session_id: str,
    *,
    on_refresh: Callable[[], None],
    key_prefix: str = "audio_",
) -> None:
    st.subheader("Audio (MVP)")
    up = st.file_uploader("Upload WAV", type=["wav"], key=f"{key_prefix}wav")
    prov = st.text_input("ASR provider", value="mock_asr", key=f"{key_prefix}asr")
    if "audio_preview" not in st.session_state:
        st.session_state["audio_preview"] = None
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Transcribe only", key=f"{key_prefix}tr") and up:
            try:
                raw = up.getvalue()
                st.session_state["audio_preview"] = client.user_transcribe_audio(
                    session_id,
                    raw,
                    up.name or "upload.wav",
                    save_asset=False,
                    provider_name=prov or None,
                )
            except ApiError as e:
                st.error(str(e))
    with c2:
        if st.button("Submit as user turn", key=f"{key_prefix}sub") and up:
            try:
                raw = up.getvalue()
                client.user_submit_audio(
                    session_id,
                    raw,
                    up.name or "upload.wav",
                    provider_name=prov or None,
                )
                st.session_state["audio_preview"] = None
                on_refresh()
            except ApiError as e:
                st.error(str(e))
    prev = st.session_state.get("audio_preview")
    if prev:
        st.caption("Transcribe preview")
        st.write(prev.get("transcript", ""))
