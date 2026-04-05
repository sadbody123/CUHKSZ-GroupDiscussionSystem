"""Lint and structural checks per artifact type."""

from __future__ import annotations

from typing import Any

from app.authoring.constants import AT_CURRICULUM_PACK, PROXY_NOTE


def _fid(prefix: str, n: int) -> str:
    return f"{prefix}_{n:04d}"


def lint_curriculum_pack_content(content: dict[str, Any], start_idx: int) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    i = start_idx
    pack_id = content.get("pack_id")
    if not pack_id:
        findings.append(
            {
                "finding_id": _fid("lint", i),
                "severity": "error",
                "rule_id": "pack_id_required",
                "message": "pack_id is required",
                "path": "pack_id",
                "suggested_fix": "Set a unique pack_id (must not match a built-in pack id).",
                "metadata": {},
            }
        )
        i += 1
    steps = content.get("steps") or []
    if not isinstance(steps, list) or len(steps) == 0:
        findings.append(
            {
                "finding_id": _fid("lint", i),
                "severity": "error",
                "rule_id": "steps_non_empty",
                "message": "curriculum pack must have at least one step",
                "path": "steps",
                "suggested_fix": None,
                "metadata": {},
            }
        )
        i += 1
        return findings
    orders = [s.get("order") for s in steps if isinstance(s, dict)]
    if orders != list(range(1, len(steps) + 1)):
        findings.append(
            {
                "finding_id": _fid("lint", i),
                "severity": "warning",
                "rule_id": "step_orders",
                "message": "step orders should be contiguous starting at 1",
                "path": "steps",
                "suggested_fix": "Renumber order fields",
                "metadata": {},
            }
        )
        i += 1
    all_focus: list[str] = []
    for j, st in enumerate(steps):
        if not isinstance(st, dict):
            continue
        if not (st.get("objective") or "").strip():
            findings.append(
                {
                    "finding_id": _fid("lint", i),
                    "severity": "error",
                    "rule_id": "step_objective",
                    "message": f"step {j} missing objective",
                    "path": f"steps[{j}].objective",
                    "suggested_fix": "Fill objective",
                    "metadata": {},
                }
            )
            i += 1
        crit = st.get("success_criteria") or []
        if not crit:
            findings.append(
                {
                    "finding_id": _fid("lint", i),
                    "severity": "error",
                    "rule_id": "step_success_criteria",
                    "message": f"step {j} missing success_criteria",
                    "path": f"steps[{j}].success_criteria",
                    "suggested_fix": "Add at least one criterion",
                    "metadata": {},
                }
            )
            i += 1
        all_focus.extend(st.get("focus_skills") or [])
    ts = content.get("target_skills") or []
    if not ts and not all_focus:
        findings.append(
            {
                "finding_id": _fid("lint", i),
                "severity": "warning",
                "rule_id": "focus_skills_nonempty",
                "message": "pack target_skills and step focus_skills are all empty",
                "path": "target_skills",
                "suggested_fix": "Add target_skills or per-step focus_skills",
                "metadata": {},
            }
        )
        i += 1
    return findings


def lint_topic_card_content(content: dict[str, Any], start_idx: int) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    i = start_idx
    tid = content.get("topic_id") or content.get("topicId")
    if not tid:
        findings.append(
            {
                "finding_id": _fid("lint", i),
                "severity": "error",
                "rule_id": "topic_id_required",
                "message": "topic_id is required",
                "path": "topic_id",
                "suggested_fix": None,
                "metadata": {},
            }
        )
        i += 1
    has_body = any(
        bool(content.get(k))
        for k in ("summary", "core_points", "example_hints", "stance_prompts")
    )
    if not has_body:
        findings.append(
            {
                "finding_id": _fid("lint", i),
                "severity": "warning",
                "rule_id": "topic_card_body",
                "message": "provide at least one of summary, core_points, example_hints",
                "path": ".",
                "suggested_fix": None,
                "metadata": {},
            }
        )
        i += 1
    return findings


def lint_drill_spec_content(content: dict[str, Any], start_idx: int) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    i = start_idx
    if not (content.get("target_skills") or []):
        findings.append(
            {
                "finding_id": _fid("lint", i),
                "severity": "error",
                "rule_id": "drill_target_skills",
                "message": "target_skills must be non-empty",
                "path": "target_skills",
                "suggested_fix": None,
                "metadata": {},
            }
        )
        i += 1
    if not (content.get("success_criteria") or []):
        findings.append(
            {
                "finding_id": _fid("lint", i),
                "severity": "warning",
                "rule_id": "drill_success_criteria",
                "message": "success_criteria should be non-empty",
                "path": "success_criteria",
                "suggested_fix": None,
                "metadata": {},
            }
        )
        i += 1
    if not (content.get("remediation_hints") or []):
        findings.append(
            {
                "finding_id": _fid("lint", i),
                "severity": "warning",
                "rule_id": "drill_remediation",
                "message": "remediation_hints should be non-empty",
                "path": "remediation_hints",
                "suggested_fix": None,
                "metadata": {},
            }
        )
        i += 1
    return findings


def lint_runtime_profile_content(content: dict[str, Any], start_idx: int) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    i = start_idx
    if not (content.get("profile_id") or "").strip():
        findings.append(
            {
                "finding_id": _fid("lint", i),
                "severity": "error",
                "rule_id": "profile_id_required",
                "message": "profile_id is required",
                "path": "profile_id",
                "suggested_fix": None,
                "metadata": {},
            }
        )
        i += 1
    return findings


def lint_for_artifact_type(artifact_type: str, content: dict[str, Any], start_idx: int = 0) -> list[dict[str, Any]]:
    if artifact_type == AT_CURRICULUM_PACK:
        return lint_curriculum_pack_content(content, start_idx)
    if artifact_type == "topic_card":
        return lint_topic_card_content(content, start_idx)
    if artifact_type == "drill_spec":
        return lint_drill_spec_content(content, start_idx)
    if artifact_type == "runtime_profile":
        return lint_runtime_profile_content(content, start_idx)
    # minimal pass for preset / assessment / roster / pedagogy
    if not content:
        return [
            {
                "finding_id": _fid("lint", start_idx),
                "severity": "warning",
                "rule_id": "empty_content",
                "message": "content is empty",
                "path": ".",
                "suggested_fix": "Provide JSON content",
                "metadata": {"note": PROXY_NOTE},
            }
        ]
    return []
