"""Runtime profile loader."""

from __future__ import annotations

from app.runtime.profile_loader import list_profile_ids, load_profile_yaml
from app.runtime.profile_resolver import resolve_runtime_profile


def test_list_profiles():
    ids = list_profile_ids()
    assert "default" in ids
    assert "balanced" in ids


def test_resolve_merges_default():
    p = resolve_runtime_profile("concise")
    assert p.profile_id == "concise"
    assert p.retrieval.get("top_k_by_role", {}).get("ally") == 4


def test_load_yaml():
    raw = load_profile_yaml("default")
    assert raw["profile_id"] == "default"
