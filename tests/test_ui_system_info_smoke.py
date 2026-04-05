"""Streamlit-related imports and API client system info."""

from __future__ import annotations

from unittest.mock import MagicMock

from app.ui.api_client import DiscussionApiClient


def test_streamlit_app_imports() -> None:
    import app.ui.streamlit_app as m  # noqa: F401

    assert m is not None


def test_api_client_system_info_mocked() -> None:
    c = DiscussionApiClient("http://example.test")
    c._request = MagicMock(return_value={"app_name": "x", "app_version": "0"})  # type: ignore[method-assign]
    assert c.get_system_info()["app_name"] == "x"


def test_system_info_panel_import() -> None:
    from app.ui.components import system_info_panel

    assert system_info_panel.render_system_info_panel is not None
