"""Filesystem consistency checks (non-blocking)."""

from __future__ import annotations

import uuid
from pathlib import Path
from typing import Any

from app.application.config import AppConfig, get_app_config
from app.group_sim.store.group_report_store import GroupReportStore
from app.modes.store.mode_report_store import ModeReportStore
from app.release.loaders.profile_loader import load_release_profile
from app.release.loaders.scenario_loader import load_demo_scenario
from app.runtime.session.file_store import FileSessionStore
from app.audio.analysis.pipeline.report_store import SpeechReportStore
from app.stability.schemas.consistency import ConsistencyFinding


def _fid() -> str:
    return f"cf_{uuid.uuid4().hex[:12]}"


def run_consistency_audit(profile_id: str, cfg: AppConfig | None = None) -> tuple[list[ConsistencyFinding], dict[str, Any]]:
    cfg = cfg or get_app_config()
    profile = load_release_profile(profile_id)
    findings: list[ConsistencyFinding] = []

    for sid in profile.demo_scenario_ids or []:
        try:
            load_demo_scenario(sid)
            ok = True
            msg = f"demo scenario {sid} loads"
        except Exception as e:
            ok = False
            msg = str(e)
        findings.append(
            ConsistencyFinding(
                finding_id=_fid(),
                entity_type="release",
                entity_id=sid,
                check_type="missing_ref",
                severity="error" if not ok else "info",
                passed=ok,
                message=msg,
                suggested_fix=None if ok else "Add scenario under app/release/scenarios",
            )
        )

    store = FileSessionStore(cfg.session_storage_dir)
    mode_store = ModeReportStore(cfg.mode_reports_dir)
    group_store = GroupReportStore(cfg.group_reports_dir)
    speech_store = SpeechReportStore(cfg.speech_report_dir)

    for session_id in store.list_session_ids():
        ctx = store.load(session_id)
        if not ctx:
            continue
        if ctx.learner_id:
            lp = cfg.learner_storage_dir / ctx.learner_id / "profile.json"
            ok = lp.is_file()
            findings.append(
                ConsistencyFinding(
                    finding_id=_fid(),
                    entity_type="session",
                    entity_id=session_id,
                    check_type="broken_ref",
                    severity="warning" if not ok else "info",
                    passed=ok,
                    message="learner file exists" if ok else f"learner_id set but file missing: {ctx.learner_id}",
                    suggested_fix=None if ok else "Rebuild learner or clear stale learner_id",
                )
            )
        if ctx.mode_report_id:
            mr = mode_store.load_by_session(session_id)
            ok = mr is not None
            findings.append(
                ConsistencyFinding(
                    finding_id=_fid(),
                    entity_type="session",
                    entity_id=session_id,
                    check_type="stale_artifact",
                    severity="warning" if not ok else "info",
                    passed=ok,
                    message="mode report resolvable" if ok else "mode_report_id set but report not found",
                    suggested_fix="Regenerate mode report",
                )
            )
        if ctx.group_balance_report_id:
            gr = group_store.load_by_session(session_id)
            ok = gr is not None
            findings.append(
                ConsistencyFinding(
                    finding_id=_fid(),
                    entity_type="session",
                    entity_id=session_id,
                    check_type="stale_artifact",
                    severity="warning" if not ok else "info",
                    passed=ok,
                    message="group report resolvable" if ok else "group balance report missing",
                    suggested_fix="Rebuild group report",
                )
            )
        if ctx.speech_report_id:
            sr = speech_store.load_session_report(session_id)
            ok = sr is not None
            findings.append(
                ConsistencyFinding(
                    finding_id=_fid(),
                    entity_type="session",
                    entity_id=session_id,
                    check_type="stale_artifact",
                    severity="warning" if not ok else "info",
                    passed=ok,
                    message="speech session report resolvable" if ok else "speech_report_id without session report",
                    suggested_fix="Re-run speech analysis or clear stale id",
                )
            )

    errs = sum(1 for f in findings if not f.passed and f.severity == "error")
    warns = sum(1 for f in findings if not f.passed and f.severity == "warning")
    summary = {
        "finding_count": len(findings),
        "failed_error": errs,
        "failed_warning": warns,
        "profile_id": profile_id,
    }
    return findings, summary
