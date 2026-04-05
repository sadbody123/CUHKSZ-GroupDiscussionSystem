"""Select a curriculum pack (API)."""

from __future__ import annotations

import streamlit as st

from app.ui.api_client import ApiError, DiscussionApiClient

SS_CURRICULUM_PACK_ID = "ui_curriculum_pack_id"


def render_curriculum_pack_selector(client: DiscussionApiClient) -> str | None:
    st.subheader("Curriculum pack")
    try:
        packs = client.list_curriculum_packs()
    except ApiError as e:
        st.warning(f"Curriculum API: {e}")
        return st.session_state.get(SS_CURRICULUM_PACK_ID)
    ids = [p["pack_id"] for p in packs]
    if SS_CURRICULUM_PACK_ID not in st.session_state and ids:
        st.session_state[SS_CURRICULUM_PACK_ID] = ids[0]
    if not ids:
        st.caption("No packs.")
        return None
    choice = st.selectbox("Pack", options=ids, index=ids.index(st.session_state[SS_CURRICULUM_PACK_ID]) if st.session_state.get(SS_CURRICULUM_PACK_ID) in ids else 0)
    st.session_state[SS_CURRICULUM_PACK_ID] = choice
    st.caption("Includes built-in YAML and custom JSON from curriculum storage / authoring publish.")
    return choice
