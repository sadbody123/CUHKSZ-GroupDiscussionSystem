"""Create or select a learner (local id only)."""

from __future__ import annotations

import os

import streamlit as st

from app.ui import state as ststate
from app.ui.api_client import ApiError, DiscussionApiClient


def render_learner_selector(client: DiscussionApiClient) -> str | None:
    if os.environ.get("ENABLE_LEARNER_UI_PANELS", "true").lower() not in ("1", "true", "yes"):
        return st.session_state.get(ststate.SS_LEARNER_ID)

    if ststate.SS_LEARNER_ID not in st.session_state:
        st.session_state[ststate.SS_LEARNER_ID] = None

    st.subheader("Learner")
    try:
        rows = client.list_learners()
    except ApiError:
        rows = []
    ids = [r["learner_id"] for r in rows]
    cur = st.session_state.get(ststate.SS_LEARNER_ID)
    pick = st.selectbox("Active learner", ["(none)"] + ids, index=(ids.index(cur) + 1) if cur in ids else 0)
    if pick != "(none)":
        st.session_state[ststate.SS_LEARNER_ID] = pick
    else:
        st.session_state[ststate.SS_LEARNER_ID] = None

    with st.expander("Create learner"):
        nid = st.text_input("New learner id", value="learner_local_001")
        dn = st.text_input("Display name (optional)")
        if st.button("Create"):
            try:
                client.create_learner(nid.strip(), display_name=dn or None)
                st.session_state[ststate.SS_LEARNER_ID] = nid.strip()
                st.success("Created")
                st.rerun()
            except ApiError as e:
                st.error(str(e))
    return st.session_state.get(ststate.SS_LEARNER_ID)
