"""Minimal Authoring Studio section (API-driven)."""

from __future__ import annotations

import streamlit as st

from app.ui.api_client import ApiError, DiscussionApiClient


def render_authoring_studio_panel(client: DiscussionApiClient, *, snapshot_id: str | None) -> None:
    st.subheader("Authoring Studio")
    st.caption("Drafts, validation, preview, and publications (phase 16). Built-in packs are never overwritten.")
    try:
        arts = client.list_authoring_artifacts(artifact_type="curriculum_pack")
    except ApiError as e:
        st.warning(f"Authoring API: {e}")
        return
    st.caption(f"Authorable curriculum packs listed: {len(arts)}")
    draft_id = st.text_input("Draft id", value="ui_authoring_draft_01")
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("Create derivative (foundation pack)"):
            try:
                r = client.create_authoring_draft(
                    draft_id=draft_id,
                    artifact_type="curriculum_pack",
                    artifact_id="foundation_gd_pack",
                    as_derivative=True,
                    author_id="ui_author",
                )
                st.success("Draft created")
                st.json(r.get("draft") or r)
            except ApiError as e:
                st.error(str(e))
    with col_b:
        if st.button("Validate draft"):
            try:
                r = client.validate_authoring_draft(draft_id)
                st.json(r.get("report") or r)
            except ApiError as e:
                st.error(str(e))
    if st.button("Preview (pack walkthrough)"):
        try:
            r = client.preview_authoring_draft(
                draft_id,
                preview_kind="pack_walkthrough",
                snapshot_id=snapshot_id,
            )
            st.json(r.get("result") or r)
        except ApiError as e:
            st.error(str(e))
    pv = st.text_input("Published version", value="1.0.0")
    if st.button("Publish draft"):
        try:
            r = client.publish_authoring_draft(draft_id, published_version=pv)
            st.json(r.get("publication") or r)
        except ApiError as e:
            st.error(str(e))
    try:
        pubs = client.list_authoring_publications()
        st.caption(f"Publications: {len(pubs)}")
        st.dataframe(pubs[:20] if pubs else [])
    except ApiError:
        pass
    try:
        patches = client.list_authoring_patches()
        if patches:
            st.caption("Patch proposals (latest)")
            st.json(patches[:5])
    except ApiError:
        pass
