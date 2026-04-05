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
        label = t.get("speaker_display_name") or t.get("speaker_name") or role
        team = t.get("team_id")
        rel = t.get("turn_relation_to_user")
        text = str(t.get("text", ""))
        im = t.get("input_mode") or "text"
        bits: list[str] = []
        if im and im != "text":
            bits.append(f"input={im}")
        if t.get("audio_asset_id"):
            bits.append("has upload audio")
        if t.get("tts_asset_id"):
            bits.append("has TTS")
        suffix = f" _({', '.join(bits)})_" if bits else ""
        who = f"{label}"
        if team:
            who += f" [{team}]"
        if rel and rel != "self":
            who += f" ({rel})"
        st.markdown(f"**{who}** (`{role}`): {text}{suffix}")
