from __future__ import annotations

from app.curriculum.engines.launch_bridge import build_session_launch_kwargs
from app.curriculum.loaders.yaml_loader import load_builtin_pack


def test_launch_bridge_keys() -> None:
    pk = load_builtin_pack("foundation_gd_pack")
    assert pk
    kw = build_session_launch_kwargs(pk, "step_foundation_01", learner_id="l", snapshot_id="dev_snapshot_v2")
    assert kw["topic_id"]
    assert kw["snapshot_id"] == "dev_snapshot_v2"
