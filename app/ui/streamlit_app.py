"""Streamlit Web MVP — talks to FastAPI via DiscussionApiClient."""

from __future__ import annotations

import streamlit as st

from app.ui.api_client import ApiError, DiscussionApiClient
from app.ui.components import controls_panel, debug_panel, session_panel, snapshot_selector, topic_selector
from app.ui.components import feedback_panel as fb_panel
from app.ui.components import transcript_panel
from app.ui.config import get_ui_config
from app.ui import state as ststate


def _client() -> DiscussionApiClient:
    cfg = get_ui_config()
    return DiscussionApiClient(cfg.api_base_url)


def main() -> None:
    st.set_page_config(page_title="Group Discussion", layout="wide")
    st.title("CUHKSZ Group Discussion (MVP)")

    cfg = get_ui_config()
    st.caption(f"API: {cfg.api_base_url}")

    try:
        client = _client()
        health = client.get_health()
        st.sidebar.success(f"API {health.get('version', '?')} — provider default: {health.get('default_provider')}")
    except ApiError as e:
        st.sidebar.error(f"Cannot reach API: {e}")
        st.stop()

    if ststate.SS_SNAPSHOT_ID not in st.session_state:
        st.session_state[ststate.SS_SNAPSHOT_ID] = None
    if ststate.SS_SESSION_ID not in st.session_state:
        st.session_state[ststate.SS_SESSION_ID] = None

    col_left, col_right = st.columns([1, 2])

    with col_left:
        st.subheader("1. Snapshot & topic")
        snap = snapshot_selector.render_snapshot_selector(client)
        if snap:
            st.session_state[ststate.SS_SNAPSHOT_ID] = snap
            topic_id, _card = topic_selector.render_topic_selector(client, snap)
            if topic_id:
                session_panel.render_session_creator(client, snap, topic_id)

    session_id = st.session_state.get(ststate.SS_SESSION_ID)

    def refresh() -> None:
        st.rerun()

    status = None
    if session_id:
        try:
            status = client.get_session(session_id)
        except ApiError:
            status = None

    with col_right:
        if session_id and status:
            transcript_panel.render_transcript(status.get("latest_turns") or [])
            controls_panel.render_controls(client, session_id, on_refresh=refresh)
            st.divider()
            if status.get("coach_report_present") and status.get("coach_text_preview"):
                st.subheader("Coach report")
                st.write(status.get("coach_text_preview"))
            else:
                fb_panel.render_feedback_panel(status)
        elif session_id:
            st.warning("Session not found — create a new one.")
        else:
            st.info("Create a session to start.")

    with st.sidebar:
        debug_panel.render_debug_panel(status)


if __name__ == "__main__":
    main()
