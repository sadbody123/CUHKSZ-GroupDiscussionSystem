"""Session replay modes."""

from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory

from app.evals.config import resolve_path
from app.evals.loaders.session_replay_loader import load_session_export
from app.evals.runners import e2e_runner
from app.evals.schemas.case import EvalCase
from app.runtime.evaluation.analyzers import analyze_transcript_turns
from app.runtime.orchestrator.state_machine import SessionStateMachine
from app.runtime.profile_resolver import resolve_runtime_profile
from app.runtime.retrieval.router import RoleRouter, build_repositories
from app.runtime.snapshot_loader import load_snapshot


def replay_analyze(session_file: Path, profile_id: str, snapshot_dir: Path) -> dict:
    ctx = load_session_export(resolve_path(session_file))
    prof = resolve_runtime_profile(profile_id)
    m_new, sig_new = analyze_transcript_turns(ctx.turns, analyzer_config=dict(prof.analyzer))
    out: dict = {"metrics": m_new, "signals": sig_new, "profile_id": prof.profile_id}
    if ctx.coach_report:
        out["previous_coach_text_len"] = len(str(ctx.coach_report.get("text", "")))
    return out


def replay_plan_turn(session_file: Path, profile_id: str, snapshot_dir: Path) -> dict:
    ctx = load_session_export(resolve_path(session_file))
    prof = resolve_runtime_profile(profile_id)
    snap = load_snapshot(Path(snapshot_dir))
    ped, top, ev, doc, _src = build_repositories(snap)
    router = RoleRouter(ped, top, ev, doc, snapshot_dir=snap.path)
    sm = SessionStateMachine(router, orchestration=dict(prof.orchestration))
    last = ctx.turns[-1].speaker_role if ctx.turns else None
    nr = sm.peek_next_role(ctx, last)
    return {"next_role": nr, "phase": ctx.phase, "profile_id": prof.profile_id}


def replay_full_mock(session_file: Path, profile_id: str, snapshot_dir: Path) -> dict:
    ctx = load_session_export(resolve_path(session_file))
    case = EvalCase(
        case_id="replay_e2e",
        case_type="e2e_case",
        inputs={
            "topic_id": ctx.topic_id or "tc-campus-ai",
            "user_stance": ctx.user_stance,
            "initial_user_turn": ctx.turns[0].text if ctx.turns else "replay session",
            "auto_steps": 2,
            "provider_name": "mock",
        },
        expected={"feedback_generated": True},
    )
    with TemporaryDirectory() as td:
        r = e2e_runner.run_e2e_case(case, Path(snapshot_dir), profile_id, Path(td))
    return r.model_dump()


def run_replay(
    *,
    session_file: Path,
    mode: str,
    profile_id: str,
    snapshot_dir: Path,
    output_dir: Path,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    snap = Path(snapshot_dir)
    if mode == "analyze":
        data = replay_analyze(session_file, profile_id, snap)
    elif mode == "plan-turn":
        data = replay_plan_turn(session_file, profile_id, snap)
    elif mode == "full-mock":
        data = replay_full_mock(session_file, profile_id, snap)
    else:
        raise ValueError(f"Unknown replay mode: {mode}")
    (output_dir / "replay_summary.json").write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
