"""Build ReleaseManifest JSON."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from app.handover.constants import RELEASE_VERSION_DEFAULT
from app.handover.engines.release_bridge import gather_handover_context, logical_ref_key
from app.handover.schemas.manifest import ReleaseManifest


def build_release_manifest(
    profile_id: str,
    *,
    release_version: str | None = None,
    ctx: dict | None = None,
    release_svc,
    stability_svc,
    cfg,
    ops,
) -> ReleaseManifest:
    ctx = ctx or gather_handover_context(
        profile_id, cfg=cfg, release=release_svc, stability=stability_svc, ops=ops
    )
    now = datetime.now(timezone.utc).isoformat()
    rid = f"gds_{profile_id}_{uuid.uuid4().hex[:8]}"
    areas = [
        "offline_build",
        "runtime",
        "api",
        "ui",
        "eval",
        "release",
        "stability",
    ]
    refs = {
        "readiness_summary": {"overall_status": ctx["readiness"].get("overall_status")},
        "rc_go_no_go": ctx["rc_report"].get("go_no_go"),
        "stability_overall": ctx["stability_report"].get("overall_status"),
        "capability_count": len(ctx.get("capability_matrix", {}).get("capabilities", [])),
    }
    lim = [i for i in ctx.get("known_issues", []) if i.get("status") == "accepted_limitation"]
    return ReleaseManifest(
        release_id=rid,
        release_version=release_version or RELEASE_VERSION_DEFAULT,
        profile_id=profile_id,
        created_at=now,
        rc_report_ref=logical_ref_key("report", "rc_latest"),
        readiness_report_ref=logical_ref_key("report", "readiness_latest"),
        stability_report_ref=logical_ref_key("report", "stability_latest"),
        capability_matrix_ref=logical_ref_key("matrix", profile_id),
        active_snapshot_ids=ctx.get("snapshot_ids") or [],
        active_demo_scenario_ids=ctx.get("demo_scenario_ids") or [],
        included_component_areas=areas,
        included_artifact_refs=refs,
        known_limitations_ref=logical_ref_key("limitations", "known_issues") if lim else None,
        docs_bundle_ref=logical_ref_key("docs", "final_bundle"),
        metadata={"known_limitations_count": len(lim), "open_issues_count": len(ctx.get("known_issues", []))},
    )
