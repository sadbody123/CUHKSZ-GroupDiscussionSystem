"""Verify final delivery prerequisites."""

from __future__ import annotations

import subprocess
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

from app.handover.config import project_root
from app.handover.schemas.verification import DeliveryVerificationReport
from app.release.loaders.profile_loader import load_release_profile


def verify_delivery(
    profile_id: str,
    *,
    snapshot_root: Path,
    require_rc: bool = False,
) -> DeliveryVerificationReport:
    now = datetime.now(timezone.utc).isoformat()
    vid = f"vfy_{uuid.uuid4().hex[:10]}"
    checks: list[dict] = []
    failed_steps: list[str] = []
    fixes: list[str] = []
    root = project_root()

    def add(name: str, ok: bool, detail: str = "") -> None:
        checks.append({"name": name, "ok": ok, "detail": detail})
        if not ok:
            failed_steps.append(name)

    add("readme_exists", (root / "README.md").is_file(), "README.md")
    add("quickstart_exists", (root / "QUICKSTART.md").is_file(), "QUICKSTART.md")
    add("main_entry", (root / "main.py").is_file(), "main.py")

    try:
        load_release_profile(profile_id)
        add("release_profile_loadable", True, profile_id)
    except Exception as e:
        add("release_profile_loadable", False, str(e))
        fixes.append("Fix release profile YAML under app/release/profiles/")

    snap_ok = (snapshot_root / "dev_snapshot_v2" / "manifest.json").is_file()
    add("default_snapshot_manifest", snap_ok, "dev_snapshot_v2")
    if not snap_ok:
        fixes.append("Build or import dev_snapshot_v2 under snapshot root")

    try:
        r = subprocess.run(
            [sys.executable, str(root / "main.py"), "--help"],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=str(root),
        )
        add("main_cli_help", r.returncode == 0, "typer help")
    except Exception as e:
        add("main_cli_help", False, str(e))
        fixes.append("Ensure python main.py --help runs")

    overall = "ok"
    if failed_steps:
        overall = "blocked" if any(x in failed_steps for x in ("release_profile_loadable", "main_cli_help")) else "warning"
    if require_rc:
        overall = "warning"

    return DeliveryVerificationReport(
        verification_id=vid,
        created_at=now,
        release_id=None,
        profile_id=profile_id,
        overall_status=overall,
        checks=checks,
        failed_steps=failed_steps,
        suggested_fixes=fixes,
        metadata={},
    )
