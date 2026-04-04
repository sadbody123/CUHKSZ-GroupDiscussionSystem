"""Debug / status sidebar."""

from __future__ import annotations

from typing import Any

import streamlit as st


def render_debug_panel(status: dict[str, Any] | None) -> None:
    st.subheader("Debug")
    if not status:
        st.caption("No session loaded.")
        return
    st.json(
        {
            "session_id": status.get("session_id"),
            "phase": status.get("phase"),
            "runtime_profile_id": status.get("runtime_profile_id"),
            "provider": status.get("provider_name"),
            "turn_count": status.get("turn_count"),
            "coach_report": status.get("coach_report_present"),
            "peek_next": status.get("peek_next_role"),
        }
    )
