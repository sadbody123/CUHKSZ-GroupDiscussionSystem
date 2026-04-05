"""Readiness audit for a release profile."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from app.application.config import AppConfig, get_app_config
from app.curriculum.loaders.yaml_loader import load_builtin_pack
from app.ops.env_validator import validate_environment
from app.release.constants import BLOCKED, READY, WARNING
from app.release.loaders.profile_loader import load_release_profile
from app.release.loaders.scenario_loader import load_demo_scenario
from app.release.schemas.readiness import ReadinessCheck, ReadinessReport
from app.runtime.profile_loader import load_profile_yaml


def run_readiness_audit(profile_id: str, cfg: AppConfig | None = None) -> ReadinessReport:
    cfg = cfg or get_app_config()
    profile = load_release_profile(profile_id)
    now = datetime.now(timezone.utc).isoformat()
    checks: list[dict[str, Any]] = []

    def add(cid: str, cat: str, sev: str, ok: bool, msg: str, fix: str | None = None) -> None:
        checks.append(
            ReadinessCheck(
                check_id=cid,
                category=cat,
                severity=sev,
                passed=ok,
                message=msg,
                suggested_fix=fix,
            ).model_dump()
        )

    env = validate_environment()
    env_ok = env["overall_status"] == "ok"
    add(
        "env_overall",
        "env",
        "error" if not env_ok else "info",
        env_ok,
        f"validate_environment: {env['overall_status']}",
        None if env_ok else "See validate-env output",
    )

    snap_root = cfg.snapshot_root
    add("snapshot_root", "snapshots", "error", snap_root.is_dir(), "snapshot_root directory present", "Configure SNAPSHOT_ROOT")

    dev = snap_root / "dev_snapshot_v2" / "manifest.json"
    add(
        "snapshot_dev_v2",
        "snapshots",
        "warning",
        dev.is_file(),
        "dev_snapshot_v2 available" if dev.is_file() else "dev_snapshot_v2 not found (recommended for demos)",
        "Run offline build" if not dev.is_file() else None,
    )

    try:
        load_profile_yaml(cfg.default_runtime_profile)
        add("runtime_profile", "runtime", "info", True, f"profile {cfg.default_runtime_profile} loads", None)
    except Exception as e:
        add("runtime_profile", "runtime", "error", False, str(e), "Fix profiles under app/runtime/profiles")

    try:
        ok = load_builtin_pack(cfg.default_curriculum_pack_id) is not None
        add("default_curriculum_pack", "curriculum", "info", ok, f"pack {cfg.default_curriculum_pack_id}", None)
    except Exception as e:
        add("default_curriculum_pack", "curriculum", "warning", False, str(e), None)

    for sid in profile.demo_scenario_ids or []:
        try:
            load_demo_scenario(sid)
            add(f"scenario_{sid}", "release", "info", True, f"scenario {sid} defined", None)
        except Exception as e:
            add(f"scenario_{sid}", "release", "error", False, str(e), "Add scenario file")

    errs = sum(1 for c in checks if not c["passed"] and c.get("severity") == "error")
    warns = sum(1 for c in checks if not c["passed"] and c.get("severity") == "warning")
    overall = BLOCKED if errs else (WARNING if warns else READY)

    return ReadinessReport(
        report_id=f"rr_{uuid.uuid4().hex[:10]}",
        profile_id=profile_id,
        created_at=now,
        overall_status=overall,
        checks=checks,
        summary={"error_count": errs, "warning_count": warns, "check_count": len(checks)},
        recommended_actions=[] if overall == READY else ["Review failing checks"],
        metadata={},
    )
