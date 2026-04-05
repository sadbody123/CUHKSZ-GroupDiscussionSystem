"""Assignment progress and launch step."""

from __future__ import annotations

import streamlit as st

from app.ui.api_client import ApiError, DiscussionApiClient
from app.ui.components.assignment_panel import SS_ASSIGNMENT_ID
from app.ui import state as ststate


def render_assignment_progress_panel(
    client: DiscussionApiClient,
    *,
    snapshot_id: str | None,
    learner_id: str | None,
) -> None:
    st.subheader("Assignment progress")
    aid = st.session_state.get(SS_ASSIGNMENT_ID)
    if not aid:
        st.caption("Create or select an assignment.")
        return
    try:
        prog = client.get_assignment_progress(aid)
    except ApiError as e:
        st.warning(str(e))
        return
    d = prog.get("delivery") or {}
    st.metric("Completion rate", f"{float(d.get('completion_rate') or 0)*100:.0f}%")
    st.caption(f"Completed steps: {d.get('completed_steps')}/{d.get('total_steps')}")
    pack = prog.get("assignment") or {}
    steps = pack.get("step_refs") or []
    if steps:
        st.write("Steps")
        for s in steps:
            st.write(f"- {s.get('pack_step_id')}: **{s.get('status')}**")
    snap = st.session_state.get(ststate.SS_SNAPSHOT_ID) or snapshot_id
    if snap and learner_id:
        step_pick = st.selectbox("Launch step", options=[s.get("pack_step_id") for s in steps if s.get("pack_step_id")])
        if st.button("Launch session for step") and step_pick:
            try:
                out = client.launch_assignment_step(
                    aid,
                    step_pick,
                    snapshot_id=snap,
                    learner_id=learner_id,
                )
                st.session_state[ststate.SS_SESSION_ID] = out["session_id"]
                st.success(f"Session {out['session_id']}")
            except ApiError as e:
                st.error(str(e))
