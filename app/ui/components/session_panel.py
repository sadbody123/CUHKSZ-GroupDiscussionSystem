"""Session creation."""

from __future__ import annotations

import streamlit as st

from app.ui import state as ststate
from app.ui.api_client import ApiError, DiscussionApiClient
from app.ui.components import mode_selector, roster_selector


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
    learner_id = st.session_state.get(ststate.SS_LEARNER_ID)
    bind = st.checkbox("Bind to active learner", value=bool(learner_id), key=f"{key_prefix}bind_learner")

    mode_fields: dict = {}
    try:
        mode_fields = mode_selector.render_mode_selector(client, key_prefix=f"{key_prefix}mode_")
    except ApiError:
        st.caption("Mode catalog unavailable — session will use API defaults.")

    roster_fields: dict = {}
    try:
        roster_fields = roster_selector.render_roster_selector(client, key_prefix=f"{key_prefix}rost_")
    except ApiError:
        pass

    if st.button("Create session", key=f"{key_prefix}create"):
        res = client.create_session(
            snapshot_id=snapshot_id,
            topic_id=topic_id,
            user_stance=stance,
            provider_name=provider or "mock",
            runtime_profile_id=prof,
            learner_id=learner_id if bind else None,
            mode_id=mode_fields.get("mode_id"),
            preset_id=mode_fields.get("preset_id"),
            drill_id=mode_fields.get("drill_id"),
            assessment_template_id=mode_fields.get("assessment_template_id"),
            roster_template_id=roster_fields.get("roster_template_id"),
            user_participant_id=roster_fields.get("user_participant_id"),
        )
        sid = str(res["session_id"])
        st.session_state[ststate.SS_SESSION_ID] = sid
        st.success(f"Session {sid}")
        st.rerun()
    return st.session_state.get(ststate.SS_SESSION_ID)
