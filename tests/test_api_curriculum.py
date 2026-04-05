from __future__ import annotations


def test_api_list_curriculum_packs(api_client) -> None:
    r = api_client.get("/curriculum-packs")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    ids = [x["pack_id"] for x in data]
    assert "foundation_gd_pack" in ids


def test_api_get_curriculum_pack(api_client) -> None:
    r = api_client.get("/curriculum-packs/foundation_gd_pack")
    assert r.status_code == 200
    body = r.json()
    assert body["pack_id"] == "foundation_gd_pack"
    assert len(body["steps"]) >= 1


def test_api_get_curriculum_pack_404(api_client) -> None:
    r = api_client.get("/curriculum-packs/nonexistent_pack_xyz")
    assert r.status_code == 404
