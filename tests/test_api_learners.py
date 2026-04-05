from __future__ import annotations

from fastapi.testclient import TestClient


def test_learners_crud(api_client: TestClient) -> None:
    r = api_client.post("/learners", json={"learner_id": "api_l1", "display_name": "T"})
    assert r.status_code == 200
    r2 = api_client.get("/learners")
    assert r2.status_code == 200
    assert any(x.get("learner_id") == "api_l1" for x in r2.json())
    r3 = api_client.get("/learners/api_l1")
    assert r3.status_code == 200
    assert r3.json()["learner_id"] == "api_l1"
