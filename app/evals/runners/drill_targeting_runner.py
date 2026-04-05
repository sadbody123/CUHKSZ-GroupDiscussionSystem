"""drill_targeting_case — weak skills map to expected drill types."""

from __future__ import annotations

import tempfile
from pathlib import Path

from app.application.config import get_app_config
from app.application.mode_service import ModeService
from app.application.session_service import SessionService
from app.evals.schemas.case import EvalCase
from app.evals.schemas.result import EvalResult
from app.learner.store.file_store import LearnerFileStore


def run_drill_targeting_case(case: EvalCase, snapshot_dir: Path, profile_id: str) -> EvalResult:
    del snapshot_dir, profile_id
    inp = case.inputs
    exp = case.expected
    learner_id = str(inp.get("learner_id") or "eval_drill_target")
    weak = list(inp.get("weak_skills") or ["example_usage"])

    with tempfile.TemporaryDirectory() as tdir:
        tmp = Path(tdir)
        cfg = get_app_config().model_copy(
            update={
                "session_storage_dir": (tmp / "sessions").resolve(),
                "learner_storage_dir": (tmp / "learners").resolve(),
                "speech_report_dir": (tmp / "speech").resolve(),
                "mode_reports_dir": (tmp / "mode_reports").resolve(),
                "enable_learner_analytics": True,
                "enable_practice_modes": True,
            }
        )
        for d in (tmp / "sessions", tmp / "learners", tmp / "speech", tmp / "mode_reports"):
            d.mkdir(parents=True, exist_ok=True)

        svc = SessionService(cfg)
        store = LearnerFileStore(cfg.learner_storage_dir)
        try:
            store.create_learner(learner_id, display_name="Eval")
        except ValueError:
            pass
        prof = store.load_learner_profile(learner_id)
        if prof:
            prof.weak_skills = weak
            store.save_learner_profile(prof)

        msvc = ModeService(cfg, svc)
        drills = msvc.generate_drills_for_learner(learner_id)
        ids = [d["drill_id"] for d in drills]
        required = list(exp.get("required_drill_ids") or ["example_support"])
        ok = all(r in ids for r in required)
        return EvalResult(
            case_id=case.case_id,
            case_type=case.case_type,
            passed=ok,
            score=1.0 if ok else 0.0,
            details={"drill_ids": ids, "weak_skills": weak},
            metadata={"count": len(drills)},
        )
