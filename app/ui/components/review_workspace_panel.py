"""Review workspace: open pack, compare AI summary vs human entry, submit."""

from __future__ import annotations

import json

import streamlit as st

from app.ui.api_client import ApiError, DiscussionApiClient
from app.ui.components.calibration_panel import render_calibration_panel
from app.ui.components.manual_scoring_panel import render_manual_scoring_panel
from app.ui.components.override_panel import render_override_panel
from app.ui.components.review_queue_panel import SS_REVIEW_PACK_ID


def render_review_workspace_panel(
    client: DiscussionApiClient,
    session_id: str | None,
    reviewer_id: str | None,
) -> None:
    st.subheader("Review workspace")
    if not session_id:
        st.caption("Create a session to enable review.")
        return
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Create review pack for session"):
            try:
                pack = client.create_review_pack(session_id)
                st.session_state[SS_REVIEW_PACK_ID] = pack["review_pack_id"]
                st.success(f"Pack {pack['review_pack_id']}")
            except ApiError as e:
                st.error(str(e))
    pack_id = st.session_state.get(SS_REVIEW_PACK_ID)
    if not pack_id:
        st.caption("Select a pack from the queue or create one.")
        render_calibration_panel(client, session_id)
        return
    try:
        pack = client.get_review_pack(pack_id)
    except ApiError as e:
        st.error(str(e))
        return

    st.caption("Original AI-derived content is in the pack; reviewed output is produced separately after submit.")
    with st.expander("AI summary & artifacts (read-only via API)", expanded=False):
        st.json(
            {
                "ai_summary": pack.get("ai_summary"),
                "proxy_limitations": pack.get("proxy_limitations"),
                "included_session": (pack.get("included_artifacts") or {}).get("session"),
            }
        )

    rubric = render_manual_scoring_panel("ws")
    ann_raw = st.text_area("annotations (JSON list)", value="[]", height=100, key="ws_ann")
    try:
        annotations = json.loads(ann_raw)
        if not isinstance(annotations, list):
            raise ValueError
    except Exception:
        st.error("annotations must be JSON list")
        annotations = []
    overrides = render_override_panel("ws")
    notes = st.text_area("summary_notes (one per line)", value="", key="ws_notes").splitlines()

    if st.button("Submit review") and reviewer_id:
        try:
            client.submit_review(
                pack_id,
                reviewer_id=reviewer_id,
                rubric_scores=rubric,
                annotations=annotations,
                override_decisions=overrides,
                summary_notes=[n for n in notes if n.strip()],
            )
            st.success("Submitted")
        except ApiError as e:
            st.error(str(e))

    render_calibration_panel(client, session_id)
