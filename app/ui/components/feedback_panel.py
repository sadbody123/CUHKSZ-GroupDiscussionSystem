"""Coach feedback display."""

from __future__ import annotations

from typing import Any

import streamlit as st


def render_feedback_panel(status: dict[str, Any] | None) -> None:
    st.subheader("Feedback")
    if not status:
        return
    sid = status.get("session_id")
    if not sid:
        return
    # Feedback is embedded in export/session dict when coach has run — refresh via parent
    st.caption("Use **Generate feedback** in controls, then refresh session.")
