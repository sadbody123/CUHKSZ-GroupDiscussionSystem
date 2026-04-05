"""Validate drafts and produce ValidationReport."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from app.authoring.engines import lint_rules
from app.authoring.schemas.draft import AuthoringDraft
from app.authoring.schemas.validation import ValidationReport


def run_validation(draft: AuthoringDraft) -> ValidationReport:
    now = datetime.now(timezone.utc).isoformat()
    findings_raw: list[dict[str, Any]] = []
    findings_raw.extend(lint_rules.lint_for_artifact_type(draft.artifact_type, draft.content, 0))
    # Generic checks
    if not draft.content:
        findings_raw.append(
            {
                "finding_id": f"gen_{uuid.uuid4().hex[:8]}",
                "severity": "warning",
                "rule_id": "content_nonempty",
                "message": "draft content is empty",
                "path": None,
                "suggested_fix": "Add JSON content for the artifact",
                "metadata": {},
            }
        )
    errors = sum(1 for f in findings_raw if f.get("severity") == "error")
    valid = errors == 0
    return ValidationReport(
        report_id=f"vr_{uuid.uuid4().hex[:12]}",
        draft_id=draft.draft_id,
        created_at=now,
        valid=valid,
        findings=findings_raw,
        cross_ref_summary={"error_count": errors, "warning_count": len(findings_raw) - errors},
        lint_summary={"rules_evaluated": True},
        metadata={},
    )
