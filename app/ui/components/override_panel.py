"""Override decisions JSON editor."""

from __future__ import annotations

import json

import streamlit as st


def render_override_panel(key_prefix: str) -> list[dict]:
    st.caption("Override decisions (approved merges only; JSON list)")
    raw = st.text_area(
        "override_decisions",
        value="[]",
        height=140,
        key=f"{key_prefix}_ov",
    )
    try:
        data = json.loads(raw)
        return data if isinstance(data, list) else []
    except json.JSONDecodeError:
        st.error("Invalid JSON for overrides")
        return []
