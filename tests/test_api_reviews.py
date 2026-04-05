from __future__ import annotations

from fastapi.testclient import TestClient


def test_create_reviewer_api(api_client: TestClient) -> None:
    r = api_client.post(
        "/reviewers",
        json={"reviewer_id": "api_rev", "display_name": "API", "role_title": "TA"},
    )
    assert r.status_code == 200
    g = api_client.get("/reviewers/api_rev")
    assert g.status_code == 200
