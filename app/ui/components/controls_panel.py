"""User input and run controls."""

from __future__ import annotations

from collections.abc import Callable

import streamlit as st

from app.ui.api_client import DiscussionApiClient


def render_controls(
    client: DiscussionApiClient,
    session_id: str,
    *,
    on_refresh: Callable[[], None],
    key_prefix: str = "",
) -> None:
    st.subheader("Your turn")
    text = st.text_area("Message", key=f"{key_prefix}msg", height=120)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        if st.button("Submit", key=f"{key_prefix}sub"):
            if text.strip():
                client.submit_user_turn(session_id, text.strip())
                on_refresh()
    with c2:
        if st.button("Run next", key=f"{key_prefix}rn"):
            client.run_next_turn(session_id)
            on_refresh()
    with c3:
        steps = st.number_input("Auto steps", min_value=1, max_value=12, value=3, key=f"{key_prefix}steps")
        if st.button("Auto run", key=f"{key_prefix}auto"):
            client.auto_run(session_id, int(steps))
            on_refresh()
    with c4:
        if st.button("Generate feedback", key=f"{key_prefix}fb"):
            client.generate_feedback(session_id)
            on_refresh()
