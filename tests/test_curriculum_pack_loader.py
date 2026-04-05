from __future__ import annotations

from app.curriculum.loaders.yaml_loader import load_builtin_pack, list_builtin_pack_ids


def test_list_builtin_ids() -> None:
    ids = list_builtin_pack_ids()
    assert "foundation_gd_pack" in ids


def test_load_foundation() -> None:
    p = load_builtin_pack("foundation_gd_pack")
    assert p and len(p.steps) >= 1
