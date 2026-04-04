"""Streamlit / UI smoke (no browser)."""

from __future__ import annotations

import importlib


def test_streamlit_app_importable() -> None:
    m = importlib.import_module("app.ui.streamlit_app")
    assert callable(getattr(m, "main", None))


def test_api_client_url() -> None:
    from app.ui.api_client import DiscussionApiClient

    c = DiscussionApiClient("http://127.0.0.1:8000")
    assert c._url("/health") == "http://127.0.0.1:8000/health"


def test_snapshot_selector_module() -> None:
    import app.ui.components.snapshot_selector as s

    assert s.render_snapshot_selector
