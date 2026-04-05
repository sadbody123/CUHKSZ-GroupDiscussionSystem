"""Session speech report summary."""

from __future__ import annotations

import streamlit as st

from app.ui.api_client import ApiError, DiscussionApiClient


def render_delivery_feedback_panel(client: DiscussionApiClient, session_id: str) -> None:
    st.subheader("Speech report (session)")
    try:
        r = client.get_speech_report(session_id)
    except ApiError as e:
        st.caption(f"Could not load: {e}")
        return
    rep = r.get("report")
    if not rep:
        st.caption("No session speech report yet — run session analysis or feedback with speech.")
        return
    st.caption(rep.get("proxy_disclaimer", r.get("proxy_note", "")))
    agg = rep.get("aggregate_metrics") or {}
    if agg:
        st.metric("Turns analyzed", agg.get("turns_analyzed", "?"))
    risks = rep.get("risks") or []
    if risks:
        st.write("**Risks (proxy)**")
        for x in risks[:8]:
            st.write(f"- {x}")
