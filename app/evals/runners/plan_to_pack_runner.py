"""plan_to_pack_case — learning plan converts to pack with weak-skill coverage."""

from __future__ import annotations

from pathlib import Path

from app.curriculum.engines.planning_bridge import pack_from_learning_plan
from app.evals.schemas.case import EvalCase
from app.evals.schemas.result import EvalResult
from app.learner.schemas.plan import LearningPlan


def run_plan_to_pack_runner(case: EvalCase, snapshot_dir: Path, profile_id: str) -> EvalResult:
    inp = case.inputs
    exp = case.expected
    plan = LearningPlan(
        plan_id="eval_plan",
        learner_id="eval_l",
        steps=[
            {
                "step_id": "s1",
                "order": 1,
                "title": "T1",
                "objective": "O1",
                "topic_id": "tc-campus-ai",
                "focus_skills": ["interaction"],
            }
        ],
        metadata={"weak_skills": inp.get("weak_skills", ["interaction"])},
    )
    pack = pack_from_learning_plan(plan, pack_id="eval_pack_draft", display_name="Eval")
    ok = len(pack.steps) >= int(exp.get("min_steps", 1))
    if exp.get("required_focus_in_steps"):
        found = False
        for st in pack.steps:
            if any(f in (st.focus_skills or []) for f in exp["required_focus_in_steps"]):
                found = True
        ok = ok and found
    return EvalResult(
        case_id=case.case_id,
        case_type=case.case_type,
        passed=ok,
        score=1.0 if ok else 0.0,
        details={"steps": len(pack.steps)},
        metadata={},
    )
