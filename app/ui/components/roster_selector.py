"""Streamlit: roster template + user seat."""

from __future__ import annotations

from typing import Any

import streamlit as st

from app.ui.api_client import ApiClient, ApiError


def render_roster_selector(client: ApiClient, *, key_prefix: str = "rost") -> dict[str, Any]:
    try:
        rows = client.list_roster_templates()
    except ApiError:
        return {"roster_template_id": None, "user_participant_id": None}
    if not rows:
        return {"roster_template_id": None, "user_participant_id": None}
    labels = {r.get("display_name", r["roster_template_id"]): r["roster_template_id"] for r in rows}
    choice = st.selectbox(
        "Roster template (optional)",
        options=["(none)"] + list(labels.keys()),
        key=f"{key_prefix}_tpl",
    )
    if choice == "(none)":
        return {"roster_template_id": None, "user_participant_id": None}
    rid = labels[choice]
    seat = st.text_input("User participant id (seat)", value="for_a", key=f"{key_prefix}_seat")
    return {"roster_template_id": rid, "user_participant_id": seat.strip() or "for_a"}
