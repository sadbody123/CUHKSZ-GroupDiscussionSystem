"""Transcript display."""

from __future__ import annotations

from typing import Any

import streamlit as st


def render_transcript(turns: list[dict[str, Any]]) -> None:
    st.subheader("Transcript")
    if not turns:
        st.caption("No turns yet.")
        return
    for t in turns:
        role = str(t.get("speaker_role", "?"))
        text = str(t.get("text", ""))
        st.markdown(f"**{role}**: {text}")
