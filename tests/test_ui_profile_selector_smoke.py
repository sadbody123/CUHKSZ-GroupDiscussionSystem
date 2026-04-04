"""UI profile client."""

from __future__ import annotations

from app.ui.api_client import DiscussionApiClient


def test_client_has_profile_methods():
    c = DiscussionApiClient("http://127.0.0.1:9")
    assert callable(c.list_profiles)
    assert callable(c.get_profile)
