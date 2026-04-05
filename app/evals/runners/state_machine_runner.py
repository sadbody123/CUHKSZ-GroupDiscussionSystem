"""state_machine_case runner."""

from __future__ import annotations

from pathlib import Path

from app.evals.config import resolve_path
from app.evals.schemas.case import EvalCase
from app.evals.schemas.result import EvalResult
from app.runtime.orchestrator.state_machine import SessionStateMachine
from app.runtime.profile_resolver import resolve_runtime_profile
from app.runtime.retrieval.router import RoleRouter, build_repositories
from app.runtime.schemas.session import SessionContext
from app.runtime.session.store import SessionStore
from app.runtime.snapshot_loader import load_snapshot


def run_state_machine_case(case: EvalCase, snapshot_dir: Path, profile_id: str) -> EvalResult:
    inp = case.inputs
    exp = case.expected
    transcript_file = resolve_path(str(inp["transcript_file"]))
    _sid, _tid, turns = SessionStore.load_transcript_file(transcript_file)
    snap = load_snapshot(snapshot_dir)
    ped, top, ev, doc, _src = build_repositories(snap)
    router = RoleRouter(ped, top, ev, doc, snapshot_dir=snap.path)
    prof = resolve_runtime_profile(profile_id or case.runtime_profile_id)
    sm = SessionStateMachine(router, orchestration=dict(prof.orchestration))
    last = turns[-1].speaker_role if turns else str(inp.get("last_role", "user"))
    ctx = SessionContext(
        session_id="eval-sm",
        topic_id=inp.get("topic_id"),
        phase=str(inp.get("current_phase", "discussion")),
        turns=list(turns),
        runtime_profile_id=prof.profile_id,
    )
    nr = sm.peek_next_role(ctx, last)
    details = {"next_role": nr, "phase": ctx.phase}
    ok = True
    if "next_role" in exp:
        ok = ok and nr == exp["next_role"]
    if exp.get("plan_reason_contains_any"):
        reason = f"phase={ctx.phase} last={last}"
        ok = ok and any(x in reason for x in exp["plan_reason_contains_any"])
    return EvalResult(
        case_id=case.case_id,
        case_type=case.case_type,
        passed=ok,
        score=1.0 if ok else 0.0,
        details=details,
        metadata={},
    )
