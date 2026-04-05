"""retrieval_case runner."""

from __future__ import annotations

from pathlib import Path

from app.evals.schemas.case import EvalCase
from app.evals.schemas.result import EvalResult
from app.runtime.profile_resolver import resolve_runtime_profile
from app.runtime.retrieval.router import RoleRouter, build_repositories
from app.runtime.snapshot_loader import load_snapshot


def run_retrieval_case(case: EvalCase, snapshot_dir: Path, profile_id: str) -> EvalResult:
    inp = case.inputs
    exp = case.expected
    snap = load_snapshot(snapshot_dir)
    ped, top, ev, doc, _src = build_repositories(snap)
    router = RoleRouter(ped, top, ev, doc, snapshot_dir=snapshot_dir)
    prof = resolve_runtime_profile(profile_id or case.runtime_profile_id)
    pkt = router.build_context_packet(
        role=str(inp.get("role", "ally")),
        topic_id=inp.get("topic_id"),
        session_phase=str(inp.get("phase", "discussion")),
        top_k=int(inp.get("top_k", 5)),
        retrieval=dict(prof.retrieval),
    )
    details: dict = {"pedagogy_count": len(pkt.pedagogy_items), "evidence_count": len(pkt.evidence_items)}
    ok = True
    if "min_evidence_count" in exp:
        ok = ok and len(pkt.evidence_items) >= int(exp["min_evidence_count"])
    if "min_pedagogy_count" in exp:
        ok = ok and len(pkt.pedagogy_items) >= int(exp["min_pedagogy_count"])
    if exp.get("required_topic_tags") and inp.get("topic_id"):
        card = top.get_topic(str(inp["topic_id"]))
        tags = set(card.tags) if card else set()
        for t in exp["required_topic_tags"]:
            ok = ok and t in tags
    score = 1.0 if ok else 0.0
    return EvalResult(
        suite_id=None,
        case_id=case.case_id,
        case_type=case.case_type,
        passed=ok,
        score=score,
        details=details,
        metadata={"profile_id": prof.profile_id},
    )
