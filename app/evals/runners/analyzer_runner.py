"""analyzer_case runner."""

from __future__ import annotations

from app.evals.config import resolve_path
from app.evals.schemas.case import EvalCase
from app.evals.schemas.result import EvalResult
from app.runtime.evaluation.analyzers import analyze_transcript_turns
from app.runtime.profile_resolver import resolve_runtime_profile
from app.runtime.session.store import SessionStore


def run_analyzer_case(case: EvalCase, snapshot_dir: Path, profile_id: str) -> EvalResult:
    inp = case.inputs
    exp = case.expected
    transcript_file = resolve_path(str(inp["transcript_file"]))
    _sid, _tid, turns = SessionStore.load_transcript_file(transcript_file)
    prof = resolve_runtime_profile(profile_id or case.runtime_profile_id)
    _m, sigs = analyze_transcript_turns(turns, analyzer_config=dict(prof.analyzer))
    ids = {s.get("id") for s in sigs}
    details = {"signals": list(ids)}
    ok = True
    for req in exp.get("required_signals", []) or []:
        ok = ok and req in ids
    for forb in exp.get("forbidden_signals", []) or []:
        ok = ok and forb not in ids
    return EvalResult(
        case_id=case.case_id,
        case_type=case.case_type,
        passed=ok,
        score=1.0 if ok else 0.0,
        details=details,
        metadata={},
    )
