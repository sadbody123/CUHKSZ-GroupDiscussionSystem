"""Streamlit: mode / preset / drill / assessment template selection."""

from __future__ import annotations

from typing import Any

import streamlit as st

from app.ui.api_client import ApiClient, ApiError


def render_mode_selector(
    client: ApiClient,
    *,
    key_prefix: str = "mode_sel",
) -> dict[str, Any]:
    """Returns selected mode_id, preset_id, drill_id, assessment_template_id (optional)."""
    try:
        modes = client.list_modes()
    except ApiError:
        modes = []
    mode_labels = {m.get("display_name", m["mode_id"]): m["mode_id"] for m in modes}
    if not mode_labels:
        mode_labels = {"free_practice": "free_practice"}
    mode_choice = st.selectbox(
        "Practice mode",
        options=list(mode_labels.keys()),
        key=f"{key_prefix}_mode",
    )
    mode_id = mode_labels[mode_choice]

    try:
        presets = client.list_presets()
    except ApiError:
        presets = []
    preset_labels = {"(none)": None}
    preset_labels.update({p.get("display_name", p["preset_id"]): p["preset_id"] for p in presets})
    preset_choice = st.selectbox(
        "Preset (optional)",
        options=list(preset_labels.keys()),
        key=f"{key_prefix}_preset",
    )
    preset_id = preset_labels[preset_choice]

    try:
        templates = client.list_assessment_templates()
    except ApiError:
        templates = []
    tmpl_labels = {"(none)": None}
    tmpl_labels.update({t.get("display_name", t["template_id"]): t["template_id"] for t in templates})
    tmpl_choice = st.selectbox(
        "Assessment template (optional, simulation)",
        options=list(tmpl_labels.keys()),
        key=f"{key_prefix}_tmpl",
    )
    assessment_template_id = tmpl_labels[tmpl_choice]

    drill_id = st.text_input(
        "Drill ID (optional, e.g. example_support)",
        value="",
        key=f"{key_prefix}_drill",
    ).strip() or None

    return {
        "mode_id": mode_id,
        "preset_id": preset_id,
        "drill_id": drill_id,
        "assessment_template_id": assessment_template_id,
    }
