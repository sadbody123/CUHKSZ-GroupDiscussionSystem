"""Coach feedback and practice mode report display."""

from __future__ import annotations

from typing import Any

import streamlit as st

from app.ui.api_client import ApiError, DiscussionApiClient


def render_mode_report_only(client: DiscussionApiClient | None, status: dict[str, Any] | None) -> None:
    if not client or not status:
        return
    sid = status.get("session_id")
    if not sid:
        return
    try:
        rep = client.get_session_mode_report(sid)
    except ApiError:
        return
    if not rep:
        return
    st.subheader("Practice mode report")
    st.caption("Simulation / practice summary — not a formal exam score.")
    if rep.get("strengths"):
        st.write("**Strengths:**", ", ".join(rep["strengths"]))
    if rep.get("risks"):
        st.write("**Risks:**", ", ".join(rep["risks"]))
    notes = rep.get("proxy_notes") or []
    for n in notes[:4]:
        st.info(n)


def render_feedback_panel(client: DiscussionApiClient | None, status: dict[str, Any] | None) -> None:
    st.subheader("Feedback")
    if not status:
        return
    sid = status.get("session_id")
    if not sid:
        return
    st.caption("Use **Generate feedback** in controls, then refresh session.")
    render_mode_report_only(client, status)
