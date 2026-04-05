"""Build demo kit directory."""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from app.handover.schemas.demo_kit import DemoKitManifest


def build_demo_kit(
    profile_id: str,
    output_dir: Path,
    *,
    release_export_demo_bundle,
    run_demo_scenario_fn,
    snapshot_id: str,
    topic_id: str,
    provider_name: str = "mock",
) -> DemoKitManifest:
    """release_export_demo_bundle: callable (output_dir) -> dict from ReleaseService.export_demo_bundle."""
    output_dir.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc).isoformat()
    kid = f"dk_{profile_id}_{uuid.uuid4().hex[:8]}"
    notes: list[str] = [
        "Demo kit is a stable showcase subset — not a full production deployment.",
        "Run with mock provider and local snapshot only.",
    ]
    bundle_sub = output_dir / "release_demo_bundle"
    try:
        release_export_demo_bundle(profile_id, bundle_sub)
        notes.append("Included phase-17 style demo bundle output under release_demo_bundle/.")
    except Exception as e:
        notes.append(f"Demo bundle export skipped: {e}")

    demo_dir = output_dir / "demo_results"
    demo_dir.mkdir(exist_ok=True)
    try:
        r = run_demo_scenario_fn(
            "text_core_demo",
            profile_id=profile_id,
            snapshot_id=snapshot_id,
            topic_id=topic_id,
            provider_name=provider_name,
        )
        raw = r.model_dump() if hasattr(r, "model_dump") else r
        (demo_dir / "text_core_demo.json").write_text(
            json.dumps(raw, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    except Exception as e:
        (demo_dir / "text_core_demo_error.txt").write_text(str(e), encoding="utf-8")
        notes.append("text_core_demo run failed; see demo_results/text_core_demo_error.txt")

    commands = [
        "python main.py run-api",
        "python main.py run-ui",
        "python main.py audit-release-readiness --profile-id " + profile_id,
        "python main.py run-demo-scenario --scenario-id text_core_demo --profile-id "
        + profile_id
        + " --snapshot-id "
        + snapshot_id
        + " --provider mock",
        "python main.py verify-delivery --profile-id " + profile_id,
    ]
    (output_dir / "quickstart_commands.txt").write_text("\n".join(commands) + "\n", encoding="utf-8")
    (output_dir / "DEMO_NOTES.md").write_text(
        "\n".join(["# Demo notes", "", *["- " + n for n in notes], ""]),
        encoding="utf-8",
    )

    included = sorted(str(p.relative_to(output_dir)).replace("\\", "/") for p in output_dir.rglob("*") if p.is_file())
    return DemoKitManifest(
        demo_kit_id=kid,
        release_id=f"rel_{profile_id}",
        created_at=now,
        target_profile_id=profile_id,
        demo_scenario_ids=["text_core_demo"],
        sample_snapshot_id=snapshot_id,
        sample_session_refs=[],
        quickstart_commands=commands,
        included_paths=included[:50],
        notes=notes,
        metadata={},
    )
