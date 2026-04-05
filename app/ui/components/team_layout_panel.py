"""Team / seat layout from session status."""

from __future__ import annotations

from typing import Any

import streamlit as st


def render_team_layout_panel(status: dict[str, Any] | None) -> None:
    if not status or not status.get("participants"):
        return
    st.subheader("Team layout (simulation)")
    for p in status.get("participants") or []:
        rel = p.get("relation_to_user") or "?"
        st.caption(f"{p.get('seat_label', '')} **{p.get('display_name', p.get('participant_id'))}** — {rel} — team `{p.get('team_id')}`")
