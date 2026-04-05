"""Create and list assignments."""

from __future__ import annotations

import streamlit as st

from app.ui.api_client import ApiError, DiscussionApiClient

SS_ASSIGNMENT_ID = "ui_assignment_id"


def render_assignment_panel(client: DiscussionApiClient, learner_id: str | None, pack_id: str | None) -> None:
    st.subheader("Assignments (training delivery)")
    if not learner_id:
        st.caption("Select a learner to create assignments.")
        return
    title = st.text_input("New assignment title", value="Week practice", key="asg_title")
    if st.button("Create assignment from pack") and pack_id:
        try:
            a = client.create_assignment(
                pack_id=pack_id,
                learner_ids=[learner_id],
                title=title,
                created_by="ui_user",
            )
            st.session_state[SS_ASSIGNMENT_ID] = a["assignment_id"]
            st.success(f"Created {a['assignment_id']}")
        except ApiError as e:
            st.error(str(e))
    try:
        rows = client.list_assignments(learner_id=learner_id)
    except ApiError as e:
        st.warning(str(e))
        return
    if not rows:
        st.caption("No assignments yet.")
        return
    opts = {r["assignment_id"]: f"{r.get('title', '')} ({r.get('status')})" for r in rows}
    pick = st.selectbox("Your assignments", options=list(opts.keys()), format_func=lambda k: opts[k])
    if pick:
        st.session_state[SS_ASSIGNMENT_ID] = pick
