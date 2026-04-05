"""demo_kit_case — demo kit contains commands and sample outputs."""

from __future__ import annotations

import tempfile
from pathlib import Path

from app.application.config import get_app_config
from app.application.handover_service import HandoverService
from app.evals.schemas.case import EvalCase
from app.evals.schemas.result import EvalResult


def run_demo_kit_case(case: EvalCase, snapshot_dir: Path, profile_id: str) -> EvalResult:
    exp = case.expected or {}
    pid = case.inputs.get("profile_id") or profile_id
    cfg = get_app_config()
    svc = HandoverService(cfg)
    with tempfile.TemporaryDirectory() as td:
        out_dir = Path(td) / "demo_kit"
        svc.build_demo_kit(pid, out_dir)
        man = out_dir / "demo_kit_manifest.json"
        qs = out_dir / "quickstart_commands.txt"
        ok = man.is_file() and qs.is_file()
        if exp.get("require_quickstart_commands"):
            import json

            raw = json.loads(man.read_text(encoding="utf-8"))
            cmds = raw.get("quickstart_commands") or []
            ok = ok and len(cmds) >= int(exp.get("min_quickstart_commands", 1))
    return EvalResult(
        case_id=case.case_id,
        case_type=case.case_type,
        passed=ok,
        score=1.0 if ok else 0.0,
        details={"demo_kit_manifest": ok},
        metadata={"profile_id": pid},
    )
