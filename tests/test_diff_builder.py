from __future__ import annotations

from app.authoring.engines.diff_builder import build_diff


def test_diff_dict_change() -> None:
    ch = build_diff({"a": 1}, {"a": 2})
    assert any(c["kind"] == "change" for c in ch)
