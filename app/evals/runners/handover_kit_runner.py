"""handover_kit_case — assembled kit includes manifest, BOM, acceptance, verification."""

from __future__ import annotations

import tempfile
from pathlib import Path

from app.application.config import get_app_config
from app.application.handover_service import HandoverService
from app.evals.schemas.case import EvalCase
from app.evals.schemas.result import EvalResult


def run_handover_kit_case(case: EvalCase, snapshot_dir: Path, profile_id: str) -> EvalResult:
    exp = case.expected or {}
    pid = case.inputs.get("profile_id") or profile_id
    cfg = get_app_config()
    svc = HandoverService(cfg)
    required = exp.get("required_relative_files") or [
        "handover_kit_manifest.json",
        "release_manifest.json",
        "bill_of_materials.json",
        "acceptance_evidence.json",
        "delivery_verification.json",
    ]
    with tempfile.TemporaryDirectory() as td:
        out = Path(td) / "kit"
        try:
            svc.build_handover_kit(pid, out)
        except Exception as e:
            return EvalResult(
                case_id=case.case_id,
                case_type=case.case_type,
                passed=False,
                score=0.0,
                details={"error": str(e)},
                metadata={"profile_id": pid},
            )
        ok = all((out / name).is_file() for name in required)
    return EvalResult(
        case_id=case.case_id,
        case_type=case.case_type,
        passed=ok,
        score=1.0 if ok else 0.0,
        details={"required_files_present": ok},
        metadata={"profile_id": pid},
    )
