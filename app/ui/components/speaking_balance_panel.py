"""Speaking balance summary."""

from __future__ import annotations

import streamlit as st

from app.ui.api_client import ApiClient, ApiError


def render_speaking_balance_panel(client: ApiClient, session_id: str | None) -> None:
    if not session_id:
        return
    st.subheader("Speaking balance (practice)")
    try:
        bal = client.get_session_balance(session_id)
    except ApiError as e:
        st.caption(f"Balance unavailable: {e}")
        return
    for p in bal.get("participant_stats") or []:
        st.caption(f"`{p.get('participant_id')}` turns={p.get('turn_count')} chars≈{p.get('total_chars')}")
    for f in bal.get("balance_flags") or []:
        st.warning(str(f))
