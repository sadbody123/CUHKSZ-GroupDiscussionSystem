"""List review packs (queue-lite)."""

from __future__ import annotations

import streamlit as st

from app.ui.api_client import ApiError, DiscussionApiClient

SS_REVIEW_PACK_ID = "ui_review_pack_id"


def render_review_queue_panel(client: DiscussionApiClient, session_id: str | None) -> None:
    st.subheader("Review queue")
    try:
        packs = client.list_review_packs(session_id=session_id)
    except ApiError as e:
        st.warning(f"Could not list packs: {e}")
        return
    if not packs:
        st.caption("No review packs yet. Create one after feedback.")
        return
    opts = {p["review_pack_id"]: f"{p['review_pack_id'][:8]}… ({p['status']})" for p in packs}
    pick = st.selectbox("Review packs", options=list(opts.keys()), format_func=lambda k: opts[k])
    if pick:
        st.session_state[SS_REVIEW_PACK_ID] = pick
