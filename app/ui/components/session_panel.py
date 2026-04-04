"""Session creation."""

from __future__ import annotations

import streamlit as st

from app.ui import state as ststate
from app.ui.api_client import DiscussionApiClient


def render_session_creator(
    client: DiscussionApiClient,
    snapshot_id: str,
    topic_id: str,
    key_prefix: str = "",
) -> str | None:
    stance = st.selectbox("User stance", ["for", "against", "neutral"], key=f"{key_prefix}stance")
    provider = st.text_input("Provider", value="mock", key=f"{key_prefix}prov")
    try:
        profs = client.list_profiles()
        pids = [p["profile_id"] for p in profs] or ["default"]
    except Exception:
        pids = ["default"]
    prof = st.selectbox("Runtime profile", pids, index=0, key=f"{key_prefix}prof")
    if st.button("Create session", key=f"{key_prefix}create"):
        res = client.create_session(
            snapshot_id=snapshot_id,
            topic_id=topic_id,
            user_stance=stance,
            provider_name=provider or "mock",
            runtime_profile_id=prof,
        )
        sid = str(res["session_id"])
        st.session_state[ststate.SS_SESSION_ID] = sid
        st.success(f"Session {sid}")
        st.rerun()
    return st.session_state.get(ststate.SS_SESSION_ID)
