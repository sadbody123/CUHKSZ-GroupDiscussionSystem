"""Select or create local reviewer profile (API-backed)."""

from __future__ import annotations

import streamlit as st

from app.ui.api_client import ApiError, DiscussionApiClient

SS_REVIEWER_ID = "ui_reviewer_id"


def render_reviewer_selector(client: DiscussionApiClient) -> str | None:
    st.subheader("Reviewer")
    try:
        rows = client.list_reviewers()
    except ApiError as e:
        st.warning(f"Review API unavailable: {e}")
        return st.session_state.get(SS_REVIEWER_ID)

    ids = [r["reviewer_id"] for r in rows]
    if SS_REVIEWER_ID not in st.session_state:
        st.session_state[SS_REVIEWER_ID] = ids[0] if ids else None

    c1, c2 = st.columns(2)
    with c1:
        if ids:
            choice = st.selectbox("Active reviewer", options=ids, index=0)
            st.session_state[SS_REVIEWER_ID] = choice
        else:
            st.caption("No reviewers yet — create one.")
    with c2:
        with st.expander("Create reviewer"):
            rid = st.text_input("reviewer_id", key="new_rev_id")
            name = st.text_input("display_name", key="new_rev_name")
            title = st.text_input("role_title", key="new_rev_title")
            if st.button("Create", key="create_rev_btn"):
                if rid and name:
                    try:
                        client.create_reviewer(rid, name, title or None)
                        st.session_state[SS_REVIEWER_ID] = rid
                        st.success("Created")
                        st.rerun()
                    except ApiError as ex:
                        st.error(str(ex))
    return st.session_state.get(SS_REVIEWER_ID)
