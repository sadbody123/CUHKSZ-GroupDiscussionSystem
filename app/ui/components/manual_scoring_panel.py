"""Manual rubric scoring (minimal JSON editor)."""

from __future__ import annotations

import json

import streamlit as st


def render_manual_scoring_panel(key_prefix: str) -> list[dict]:
    st.caption("Rubric scores (JSON list)")
    raw = st.text_area(
        "rubric_scores",
        value='[{"dimension_id":"content","score":4,"max_score":5,"note":"ok"}]',
        height=120,
        key=f"{key_prefix}_rubric",
    )
    try:
        data = json.loads(raw)
        return data if isinstance(data, list) else []
    except json.JSONDecodeError:
        st.error("Invalid JSON for rubric_scores")
        return []
