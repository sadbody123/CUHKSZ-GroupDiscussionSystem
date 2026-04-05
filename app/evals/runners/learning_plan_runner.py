"""learning_plan_case — plan step counts and weak-skill coverage."""

from __future__ import annotations

import json
from pathlib import Path

from app.application.config import get_app_config
from app.application.learner_service import LearnerService
from app.application.session_service import SessionService
from app.evals.schemas.case import EvalCase
from app.evals.schemas.result import EvalResult


def run_learning_plan_case(case: EvalCase, snapshot_dir: Path, profile_id: str) -> EvalResult:
    del profile_id
    inp = case.inputs
    exp = case.expected
    project_root = Path(__file__).resolve().parents[3]
    manifest_rel = Path(str(inp["manifest"]))
    manifest_path = manifest_rel if manifest_rel.is_absolute() else (project_root / manifest_rel).resolve()

    import tempfile

    with tempfile.TemporaryDirectory() as tdir:
        tmp = Path(tdir)
        cfg = get_app_config().model_copy(
            update={
                "session_storage_dir": (tmp / "sessions").resolve(),
                "learner_storage_dir": (tmp / "learners").resolve(),
                "speech_report_dir": (tmp / "speech").resolve(),
                "enable_learner_analytics": True,
                "default_learning_plan_horizon": int(inp.get("horizon") or 4),
            }
        )
        for d in (tmp / "sessions", tmp / "learners", tmp / "speech"):
            d.mkdir(parents=True, exist_ok=True)

        raw = json.loads(manifest_path.read_text(encoding="utf-8"))
        l_id = str(inp.get("learner_id") or "eval_plan")
        svc = SessionService(cfg)
        lsvc = LearnerService(cfg, svc)
        try:
            lsvc.create_learner(l_id, display_name="Eval")
        except ValueError:
            pass

        for rel in raw.get("session_files") or []:
            p = Path(str(rel))
            src = p if p.is_absolute() else (manifest_path.parent / p).resolve()
            data = json.loads(src.read_text(encoding="utf-8"))
            sid = str(data["session_id"])
            data["snapshot_dir"] = str(snapshot_dir.resolve())
            (tmp / "sessions" / f"{sid}.json").write_text(
                json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
            )
            lsvc.attach_session_to_learner(l_id, sid, ingest=True)

        plan = lsvc.generate_learning_plan(l_id, horizon=int(inp.get("horizon") or 4), persist=False)
        steps = plan.steps or []
        ok = True
        if exp.get("min_plan_steps") is not None:
            ok = ok and len(steps) >= int(exp["min_plan_steps"])
        prof = lsvc.get_learner_profile(l_id)
        weak = list(prof.weak_skills or []) if prof else []
        cover = exp.get("weak_skill_covered_in_plan") or []
        for w in cover:
            ok = ok and any(w in str(s) for s in steps)
        pid = exp.get("recommended_profile_in")
        if pid:
            ok = ok and any((st.get("runtime_profile_id") == pid) for st in steps if isinstance(st, dict))
        mode = exp.get("recommended_mode_in")
        if mode:
            ok = ok and any((st.get("mode") == mode) for st in steps if isinstance(st, dict))
        return EvalResult(
            case_id=case.case_id,
            case_type=case.case_type,
            passed=ok,
            score=1.0 if ok else 0.0,
            details={"plan_steps": len(steps), "weak_skills": weak},
            metadata={"plan_id": plan.plan_id},
        )
