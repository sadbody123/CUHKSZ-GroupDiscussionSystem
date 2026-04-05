"""Calibration summary from API."""

from __future__ import annotations

import streamlit as st

from app.ui.api_client import ApiError, DiscussionApiClient


def render_calibration_panel(client: DiscussionApiClient, session_id: str | None) -> None:
    st.subheader("Calibration (AI vs human)")
    if not session_id:
        st.caption("Need session.")
        return
    try:
        summ = client.get_session_review_summary(session_id)
        cal = client.get_session_calibration(session_id)
    except ApiError as e:
        st.warning(str(e))
        return
    st.caption(f"Reviews recorded: {summ.get('review_count', 0)}")
    if cal:
        st.metric("Overall agreement", cal.get("overall_agreement") or "n/a")
        st.write("Key mismatches", cal.get("key_mismatches") or [])
    else:
        st.caption("No calibration yet — submit a review first.")
