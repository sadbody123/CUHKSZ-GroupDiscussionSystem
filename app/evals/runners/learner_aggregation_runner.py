"""learner_aggregation_case — profile weak/strong skills from sessions."""

from __future__ import annotations

import json
from pathlib import Path

from app.application.config import get_app_config
from app.application.learner_service import LearnerService
from app.application.session_service import SessionService
from app.evals.schemas.case import EvalCase
from app.evals.schemas.result import EvalResult


def run_learner_aggregation_case(case: EvalCase, snapshot_dir: Path, profile_id: str) -> EvalResult:
    del profile_id
    inp = case.inputs
    exp = case.expected
    project_root = Path(__file__).resolve().parents[3]
    manifest_rel = Path(str(inp["manifest"]))
    manifest_path = manifest_rel if manifest_rel.is_absolute() else (project_root / manifest_rel).resolve()
    raw = json.loads(manifest_path.read_text(encoding="utf-8"))
    session_files = list(raw.get("session_files") or [])

    import tempfile

    with tempfile.TemporaryDirectory() as tdir:
        tmp = Path(tdir)
        sess_root = tmp / "sessions"
        learn_root = tmp / "learners"
        speech_root = tmp / "speech_reports"
        for d in (sess_root, learn_root, speech_root):
            d.mkdir(parents=True, exist_ok=True)

        cfg = get_app_config().model_copy(
            update={
                "session_storage_dir": sess_root.resolve(),
                "learner_storage_dir": learn_root.resolve(),
                "speech_report_dir": speech_root.resolve(),
                "enable_learner_analytics": True,
            }
        )
        l_id = str(inp.get("learner_id") or "eval_learner_agg")
        svc = SessionService(cfg)
        lsvc = LearnerService(cfg, svc)
        try:
            lsvc.create_learner(l_id, display_name="Eval")
        except ValueError:
            pass

        for rel in session_files:
            p = Path(str(rel))
            src = p if p.is_absolute() else (manifest_path.parent / p).resolve()
            data = json.loads(src.read_text(encoding="utf-8"))
            sid = str(data["session_id"])
            data["snapshot_dir"] = str(snapshot_dir.resolve())
            (sess_root / f"{sid}.json").write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            lsvc.attach_session_to_learner(l_id, sid, ingest=True)

        prof = lsvc.get_learner_profile(l_id)
        ok = prof is not None
        weak = list(prof.weak_skills or []) if prof else []
        if exp.get("min_total_sessions") is not None:
            ok = ok and int(prof.total_sessions if prof else 0) >= int(exp["min_total_sessions"])
        for w in exp.get("required_weak_skills") or []:
            ok = ok and w in weak
        for f in exp.get("forbidden_weak_skills") or []:
            ok = ok and f not in weak
        return EvalResult(
            case_id=case.case_id,
            case_type=case.case_type,
            passed=ok,
            score=1.0 if ok else 0.0,
            details={"weak_skills": weak, "total_sessions": prof.total_sessions if prof else 0},
            metadata={"learner_id": l_id},
        )
