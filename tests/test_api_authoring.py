from __future__ import annotations


def test_authoring_artifacts_endpoint(api_client) -> None:
    r = api_client.get("/authoring/artifacts", params={"artifact_type": "curriculum_pack"})
    assert r.status_code == 200
    assert isinstance(r.json(), list)
