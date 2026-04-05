from __future__ import annotations

from app.authoring.engines.patch_generator import apply_ops_to_content, generate_patches_from_curriculum_gap


def test_apply_ops_set() -> None:
    out = apply_ops_to_content({"x": 1}, [{"op": "set", "path": "x", "value": 2}])
    assert out["x"] == 2


def test_curriculum_gap_patches() -> None:
    ps = generate_patches_from_curriculum_gap(assignment_id="a1", completed_steps=0, total_steps=3)
    assert len(ps) == 1
