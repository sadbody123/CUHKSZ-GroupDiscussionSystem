"""Run an eval suite and build a report."""

from __future__ import annotations

import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path

from app.evals.loaders.dataset_loader import load_case
from app.evals.loaders.suite_loader import load_suite
from app.evals.reporters import csv_reporter, json_reporter, markdown_reporter
from app.evals.runners import (
    agent_runner,
    analyzer_runner,
    assessment_simulation_runner,
    assignment_progress_runner,
    audio_roundtrip_runner,
    authoring_lineage_runner,
    authoring_patch_runner,
    authoring_preview_case_runner,
    authoring_publication_runner,
    authoring_validation_runner,
    calibration_runner,
    capability_matrix_runner,
    curriculum_pack_runner,
    demo_scenario_eval_runner,
    delivery_report_runner,
    disagreement_runner,
    drill_targeting_runner,
    e2e_runner,
    indexed_retrieval_runner,
    learner_aggregation_runner,
    learning_plan_runner,
    launch_bridge_runner,
    mode_flow_runner,
    override_merge_runner,
    plan_to_pack_runner,
    readiness_runner,
    recommendation_runner,
    retrieval_runner,
    review_pack_runner,
    scope_freeze_runner,
    seat_allocation_runner,
    speech_delivery_runner,
    state_machine_runner,
    consistency_runner,
    e2e_flow_runner,
    recovery_policy_runner,
    rc_gate_runner,
    release_manifest_runner,
    demo_kit_runner,
    handover_kit_runner,
    delivery_verification_runner,
    acceptance_evidence_runner,
)
from app.evals.schemas.report import EvalReport


def _dispatch(case_type: str):
    return {
        "retrieval_case": retrieval_runner.run_retrieval_case,
        "indexed_retrieval_case": indexed_retrieval_runner.run_indexed_retrieval_case,
        "state_machine_case": state_machine_runner.run_state_machine_case,
        "analyzer_case": analyzer_runner.run_analyzer_case,
        "agent_case": agent_runner.run_agent_case,
        "e2e_case": e2e_runner.run_e2e_case,
        "audio_roundtrip_case": audio_roundtrip_runner.run_audio_roundtrip_case,
        "speech_delivery_case": speech_delivery_runner.run_speech_delivery_case,
        "learner_aggregation_case": learner_aggregation_runner.run_learner_aggregation_case,
        "recommendation_case": recommendation_runner.run_recommendation_case,
        "learning_plan_case": learning_plan_runner.run_learning_plan_case,
        "mode_flow_case": mode_flow_runner.run_mode_flow_case,
        "drill_targeting_case": drill_targeting_runner.run_drill_targeting_case,
        "assessment_simulation_case": assessment_simulation_runner.run_assessment_simulation_case,
        "seat_allocation_case": seat_allocation_runner.run_seat_allocation_case,
        "review_pack_case": review_pack_runner.run_review_pack_case,
        "override_merge_case": override_merge_runner.run_override_merge_case,
        "calibration_case": calibration_runner.run_calibration_case,
        "disagreement_case": disagreement_runner.run_disagreement_case,
        "curriculum_pack_case": curriculum_pack_runner.run_curriculum_pack_case,
        "assignment_progress_case": assignment_progress_runner.run_assignment_progress_case,
        "launch_bridge_case": launch_bridge_runner.run_launch_bridge_case,
        "plan_to_pack_case": plan_to_pack_runner.run_plan_to_pack_runner,
        "delivery_report_case": delivery_report_runner.run_delivery_report_case,
        "authoring_validation_case": authoring_validation_runner.run_authoring_validation_case,
        "patch_proposal_case": authoring_patch_runner.run_patch_proposal_case,
        "preview_case": authoring_preview_case_runner.run_preview_case,
        "publication_case": authoring_publication_runner.run_publication_case,
        "lineage_case": authoring_lineage_runner.run_lineage_case,
        "readiness_case": readiness_runner.run_readiness_case,
        "capability_matrix_case": capability_matrix_runner.run_capability_matrix_case,
        "demo_scenario_case": demo_scenario_eval_runner.run_demo_scenario_case,
        "scope_freeze_case": scope_freeze_runner.run_scope_freeze_case,
        "consistency_case": consistency_runner.run_consistency_case,
        "e2e_flow_case": e2e_flow_runner.run_e2e_flow_case,
        "recovery_policy_case": recovery_policy_runner.run_recovery_policy_case,
        "rc_gate_case": rc_gate_runner.run_rc_gate_case,
        "release_manifest_case": release_manifest_runner.run_release_manifest_case,
        "demo_kit_case": demo_kit_runner.run_demo_kit_case,
        "handover_kit_case": handover_kit_runner.run_handover_kit_case,
        "delivery_verification_case": delivery_verification_runner.run_delivery_verification_case,
        "acceptance_evidence_case": acceptance_evidence_runner.run_acceptance_evidence_case,
    }.get(case_type)


def run_eval_suite(
    *,
    suite_file: Path,
    snapshot_dir: Path,
    profile_id: str,
    output_dir: Path,
) -> EvalReport:
    suite = load_suite(suite_file)
    prof = profile_id or suite.default_runtime_profile_id or "default"
    output_dir.mkdir(parents=True, exist_ok=True)
    results: list[dict] = []
    with tempfile.TemporaryDirectory() as tdir:
        tmp = Path(tdir)
        for ref in suite.case_refs:
            case = load_case(ref)
            fn = _dispatch(case.case_type)
            if not fn:
                raise ValueError(f"Unknown case_type: {case.case_type}")
            if case.case_type in ("e2e_case", "audio_roundtrip_case", "speech_delivery_case"):
                r = fn(case, snapshot_dir, prof, tmp)
            else:
                r = fn(case, snapshot_dir, prof)
            row = r.model_dump()
            row["profile_id"] = prof
            results.append(row)

    passed = sum(1 for x in results if x.get("passed"))
    report = EvalReport(
        report_id=str(uuid.uuid4()),
        created_at=datetime.now(timezone.utc).isoformat(),
        suite_id=suite.suite_id,
        profile_ids=[prof],
        total_cases=len(results),
        passed_cases=passed,
        failed_cases=len(results) - passed,
        summary={"suite": suite.suite_id, "profile": prof},
        results=results,
        metadata={},
    )
    json_reporter.write(output_dir / "report.json", report)
    markdown_reporter.write(output_dir / "report.md", report)
    csv_reporter.write(output_dir / "report.csv", report)
    return report


def compare_profiles(
    *,
    suite_file: Path,
    snapshot_dir: Path,
    profiles: list[str],
    output_dir: Path,
) -> EvalReport:
    """Run the same suite for multiple profiles; aggregate one report."""
    output_dir.mkdir(parents=True, exist_ok=True)
    all_results: list[dict] = []
    suite = load_suite(suite_file)
    for pid in profiles:
        sub = output_dir / pid
        r = run_eval_suite(suite_file=suite_file, snapshot_dir=snapshot_dir, profile_id=pid, output_dir=sub)
        for row in r.results:
            row = {**row, "profile_id": pid}
            all_results.append(row)
    passed = sum(1 for x in all_results if x.get("passed"))
    report = EvalReport(
        report_id=str(uuid.uuid4()),
        created_at=datetime.now(timezone.utc).isoformat(),
        suite_id=suite.suite_id,
        profile_ids=list(profiles),
        total_cases=len(all_results),
        passed_cases=passed,
        failed_cases=len(all_results) - passed,
        summary={"mode": "compare_profiles", "profiles": profiles},
        results=all_results,
        metadata={},
    )
    json_reporter.write(output_dir / "report.json", report)
    markdown_reporter.write(output_dir / "report.md", report)
    csv_reporter.write(output_dir / "report.csv", report)
    return report
