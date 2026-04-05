"""Build acceptance evidence from bridge context."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from app.handover.engines.release_bridge import gather_handover_context
from app.handover.schemas.acceptance import AcceptanceEvidence


def build_acceptance_evidence(
    profile_id: str,
    *,
    ctx: dict[str, Any] | None = None,
    release_svc,
    stability_svc,
    cfg,
    ops,
) -> AcceptanceEvidence:
    ctx = ctx or gather_handover_context(
        profile_id, cfg=cfg, release=release_svc, stability=stability_svc, ops=ops
    )
    now = datetime.now(timezone.utc).isoformat()
    eid = f"acc_{uuid.uuid4().hex[:10]}"
    readiness = ctx["readiness"]
    rc = ctx["rc_report"]
    stab = ctx["stability_report"]
    passed: list[dict] = []
    failed: list[dict] = []
    if readiness.get("overall_status") != "blocked":
        passed.append({"check": "readiness_not_blocked", "detail": readiness.get("overall_status")})
    else:
        failed.append({"check": "readiness", "detail": "blocked"})
    if rc.get("go_no_go") in ("go", "conditional_go"):
        passed.append({"check": "rc_gate", "detail": rc.get("go_no_go")})
    else:
        failed.append({"check": "rc_gate", "detail": rc.get("go_no_go")})
    if stab.get("overall_status") in ("green", "yellow"):
        passed.append({"check": "stability", "detail": stab.get("overall_status")})
    else:
        failed.append({"check": "stability", "detail": stab.get("overall_status")})
    lim_lines = [
        f"{i.get('issue_id')}: {i.get('title')}"
        for i in ctx.get("known_issues", [])
        if i.get("status") == "accepted_limitation"
    ]
    return AcceptanceEvidence(
        evidence_id=eid,
        created_at=now,
        release_id=f"rel_{profile_id}",
        profile_id=profile_id,
        readiness_ref="readiness:latest",
        consistency_ref="consistency:latest",
        stability_ref="stability:latest",
        rc_ref="rc:latest",
        demo_result_refs=["demo:text_core_demo"],
        passed_checks=passed,
        failed_checks=failed,
        accepted_limitations=lim_lines,
        summary={
            "readiness_status": readiness.get("overall_status"),
            "rc_go_no_go": rc.get("go_no_go"),
            "stability_overall": stab.get("overall_status"),
        },
        metadata={"note": "Advisory evidence for local handover — not formal certification."},
    )
