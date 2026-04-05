from __future__ import annotations

from app.curriculum.engines.assignment_planner import plan_assignment_from_pack
from app.curriculum.loaders.yaml_loader import load_builtin_pack


def test_plan_assignment() -> None:
    pk = load_builtin_pack("foundation_gd_pack")
    assert pk
    spec = plan_assignment_from_pack(pk, learner_ids=["l1"], title="t", created_by="x")
    assert spec.total_steps == len(pk.steps)
    assert spec.step_refs
