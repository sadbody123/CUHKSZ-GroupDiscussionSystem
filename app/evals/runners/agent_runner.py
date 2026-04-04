"""agent_case runner (mock provider)."""

from __future__ import annotations

from app.evals.config import resolve_path
from app.evals.schemas.case import EvalCase
from app.evals.schemas.result import EvalResult
from app.runtime.agents.base import run_agent_turn
from app.runtime.llm.manager import get_provider
from app.runtime.profile_resolver import resolve_runtime_profile
from app.runtime.retrieval.router import RoleRouter, build_repositories
from app.runtime.schemas.session import SessionContext
from app.runtime.session.store import SessionStore
from app.runtime.snapshot_loader import load_snapshot


def run_agent_case(case: EvalCase, snapshot_dir: Path, profile_id: str) -> EvalResult:
    inp = case.inputs
    exp = case.expected
    transcript_file = resolve_path(str(inp["transcript_file"]))
    _sid, _tid, turns = SessionStore.load_transcript_file(transcript_file)
    snap = load_snapshot(snapshot_dir)
    ped, top, ev, doc, _src = build_repositories(snap)
    router = RoleRouter(ped, top, ev, doc)
    prof = resolve_runtime_profile(profile_id or case.runtime_profile_id)
    ctx = SessionContext(
        session_id="eval-agent",
        topic_id=inp.get("topic_id"),
        phase=str(inp.get("phase", "discussion")),
        turns=list(turns),
        provider_name=str(inp.get("provider_name", "mock")),
        runtime_profile_id=prof.profile_id,
    )
    role = str(inp.get("role", "ally"))
    prov = get_provider(ctx.provider_name)
    reply = run_agent_turn(router=router, provider=prov, role=role, session=ctx)
    text = reply.text.lower()
    ok = True
    for s in exp.get("text_contains_any", []) or []:
        ok = ok and s.lower() in text
    for s in exp.get("text_not_contains_any", []) or []:
        ok = ok and s.lower() not in text
    if "max_chars" in exp:
        ok = ok and len(reply.text) <= int(exp["max_chars"])
    for k in exp.get("required_metadata_keys", []) or []:
        ok = ok and k in reply.metadata
    return EvalResult(
        case_id=case.case_id,
        case_type=case.case_type,
        passed=ok,
        score=1.0 if ok else 0.0,
        details={"reply_preview": reply.text[:200]},
        metadata={"metadata_keys": list(reply.metadata.keys())},
    )
