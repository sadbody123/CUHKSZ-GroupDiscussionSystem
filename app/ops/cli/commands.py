"""Engineering / ops CLI commands (phase 7)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer

from app.application.audio_service import AudioService
from app.application.config import AppConfig
from app.application.discussion_service import DiscussionService
from app.application.feedback_service import FeedbackService
from app.application.learner_service import LearnerService
from app.application.authoring_service import AuthoringService
from app.application.curriculum_service import CurriculumService
from app.application.review_service import ReviewService
from app.curriculum.store.pack_store import PackStore
from app.application.release_service import ReleaseService
from app.application.handover_service import HandoverService
from app.application.stability_service import StabilityService
from app.application.session_service import SessionService
from app.logging import setup_logging
from app.ops.artifacts.registry import ArtifactRegistry
from app.ops.bundles.bundle_manager import export_snapshot_bundle, import_snapshot_bundle
from app.config import get_settings
from app.offline_build.build_snapshot.validators import validate_snapshot_dir
from app.offline_build.pipeline import run_offline_pipeline
from app.ops.env_validator import validate_environment


def register_ops_cli(app: typer.Typer) -> None:
    @app.command("bootstrap-dev-snapshot")
    def bootstrap_dev_snapshot_cmd(
        force: bool = typer.Option(False, "--force", "-f", help="Rebuild even if a valid snapshot already exists"),
    ) -> None:
        """Build ``dev_snapshot_v2`` from ``tests/fixtures`` (recommended before tests/demo when snapshot is missing)."""
        setup_logging()
        root = Path(__file__).resolve().parents[3]
        input_dir = root / "tests" / "fixtures" / "datahub_exports"
        pedagogy_dir = root / "tests" / "fixtures" / "pedagogy"
        topic_card_dir = root / "tests" / "fixtures" / "topic_cards"
        snapshot_id = "dev_snapshot_v2"
        if not input_dir.is_dir():
            typer.echo(f"ERROR: fixture exports not found: {input_dir}", err=True)
            raise typer.Exit(1)
        if not pedagogy_dir.is_dir() or not topic_card_dir.is_dir():
            typer.echo(f"ERROR: pedagogy/topic fixtures missing under tests/fixtures", err=True)
            raise typer.Exit(1)
        settings = get_settings()
        out_path = settings.snapshot_root / snapshot_id
        manifest = out_path / "manifest.json"
        if manifest.is_file() and not force:
            res = validate_snapshot_dir(out_path)
            if res.ok:
                typer.echo(
                    json.dumps(
                        {
                            "status": "ok",
                            "skipped": True,
                            "snapshot_dir": str(out_path.resolve()),
                            "detail": "already present and valid (use --force to rebuild)",
                        },
                        ensure_ascii=False,
                        indent=2,
                    )
                )
                raise typer.Exit(0)
            typer.echo("WARN: existing snapshot failed validation; rebuilding.", err=True)
        out = run_offline_pipeline(
            input_dir,
            snapshot_id,
            settings=settings,
            pedagogy_dir=pedagogy_dir,
            topic_card_dir=topic_card_dir,
        )
        typer.echo(
            json.dumps(
                {"status": "ok", "skipped": False, "snapshot_dir": str(out.resolve())},
                ensure_ascii=False,
                indent=2,
            )
        )

    @app.command("validate-env")
    def validate_env_cmd() -> None:
        """Run structured environment checks (exit 1 on failure)."""
        setup_logging()
        r = validate_environment()
        typer.echo(json.dumps(r, ensure_ascii=False, indent=2))
        raise typer.Exit(0 if r["overall_status"] == "ok" else 1)

    @app.command("list-artifacts")
    def list_artifacts_cmd(
        kind: Optional[str] = typer.Option(None, "--kind", "-k", help="Filter by artifact_kind"),
    ) -> None:
        """List artifacts discovered under known directories."""
        setup_logging()
        reg = ArtifactRegistry()
        rows = reg.list_artifacts(kind=kind)
        typer.echo(json.dumps([r.model_dump() for r in rows], ensure_ascii=False, indent=2))

    @app.command("inspect-artifact")
    def inspect_artifact_cmd(
        artifact_id: Optional[str] = typer.Option(None, "--artifact-id"),
        path: Optional[Path] = typer.Option(None, "--path"),
    ) -> None:
        """Show one artifact record."""
        setup_logging()
        if not artifact_id and not path:
            typer.echo("Specify --artifact-id or --path", err=True)
            raise typer.Exit(1)
        if path is not None and not path.exists():
            typer.echo(f"path not found: {path}", err=True)
            raise typer.Exit(1)
        reg = ArtifactRegistry()
        rec = reg.inspect_artifact(artifact_id=artifact_id, path=str(path) if path else None)
        if not rec:
            typer.echo("artifact not found", err=True)
            raise typer.Exit(1)
        typer.echo(json.dumps(rec.model_dump(), ensure_ascii=False, indent=2))

    @app.command("export-snapshot-bundle")
    def export_snapshot_bundle_cmd(
        output_file: Path = typer.Option(..., "--output-file", "-o", help="Output .zip path"),
        snapshot_id: Optional[str] = typer.Option(None, "--snapshot-id", "-s"),
        snapshot_dir: Optional[Path] = typer.Option(None, "--snapshot-dir", exists=True, file_okay=False, dir_okay=True),
    ) -> None:
        """Zip a validated snapshot into a portable bundle."""
        setup_logging()
        out, manifest = export_snapshot_bundle(
            snapshot_dir=snapshot_dir,
            snapshot_id=snapshot_id,
            output_file=output_file,
        )
        typer.echo(json.dumps({"output_file": str(out), "manifest": manifest.model_dump()}, ensure_ascii=False, indent=2))

    @app.command("import-snapshot-bundle")
    def import_snapshot_bundle_cmd(
        bundle_file: Path = typer.Option(..., "--bundle-file", exists=True, dir_okay=False),
        on_conflict: str = typer.Option("fail", "--on-conflict", help="fail | overwrite | rename"),
    ) -> None:
        """Import a bundle zip into the configured snapshot root."""
        setup_logging()
        target = import_snapshot_bundle(bundle_file, on_conflict=on_conflict)
        typer.echo(json.dumps({"imported_to": str(target)}, ensure_ascii=False, indent=2))

    @app.command("run-smoke")
    def run_smoke_cmd(
        snapshot_id: str = typer.Option(..., "--snapshot-id", "-s"),
        topic_id: str = typer.Option(..., "--topic-id", "-t"),
        provider: str = typer.Option("mock", "--provider", "-p"),
        runtime_profile: str = typer.Option("default", "--runtime-profile"),
        with_audio: bool = typer.Option(False, "--with-audio"),
        with_speech_analysis: bool = typer.Option(False, "--with-speech-analysis"),
        with_learner: bool = typer.Option(False, "--with-learner"),
        with_review: bool = typer.Option(False, "--with-review"),
        with_assignment: bool = typer.Option(False, "--with-assignment"),
        with_authoring: bool = typer.Option(False, "--with-authoring"),
        mode_id: Optional[str] = typer.Option(None, "--mode-id"),
        assessment_template_id: Optional[str] = typer.Option(None, "--assessment-template-id"),
        release_profile: Optional[str] = typer.Option(None, "--release-profile"),
        respect_release_gates: bool = typer.Option(False, "--respect-release-gates"),
        with_stability_audit: bool = typer.Option(False, "--with-stability-audit"),
        final_delivery: bool = typer.Option(False, "--final-delivery"),
    ) -> None:
        """Minimal end-to-end smoke: session, turns, auto-run, feedback (mock-friendly)."""
        setup_logging()
        cfg = AppConfig.from_env()
        release_extra: dict = {}
        if release_profile:
            rsvc = ReleaseService(cfg)
            rep = rsvc.run_readiness_audit(release_profile)
            release_extra["release_profile"] = release_profile
            release_extra["release_readiness"] = rep.overall_status
            if respect_release_gates and rep.overall_status == "blocked":
                typer.echo(json.dumps(release_extra, ensure_ascii=False, indent=2))
                raise typer.Exit(1)
            try:
                dr = rsvc.run_demo_scenario(
                    "text_core_demo",
                    profile_id=release_profile,
                    snapshot_id=snapshot_id,
                    topic_id=topic_id,
                    provider_name=provider,
                )
                release_extra["release_demo_text_core"] = dr.model_dump()
            except Exception as e:
                release_extra["release_demo_error"] = str(e)
        sessions = SessionService(cfg)
        disc = DiscussionService(cfg, sessions)
        fb = FeedbackService(sessions)
        if with_authoring:
            asvc = AuthoringService(cfg, sessions)
            did = f"smoke_auth_{snapshot_id}".replace("-", "_")[:40]
            asvc.create_derivative_draft(
                draft_id=did,
                artifact_type="curriculum_pack",
                base_artifact_id=cfg.default_curriculum_pack_id,
                author_id="smoke",
            )
            asvc.validate_draft(did)
            asvc.preview_draft(did, preview_kind="pack_walkthrough", snapshot_id=snapshot_id)
            pub = asvc.publish_draft(did, published_version="0.0.1-smoke")
            d2 = asvc.get_draft(did)
            ps = PackStore(cfg.curriculum_pack_builtin_dir, cfg.curriculum_custom_pack_dir)
            pk = ps.load_pack(str(d2.content.get("pack_id")))
            typer.echo(
                json.dumps(
                    {
                        "authoring_smoke": True,
                        "draft_id": did,
                        "pack_id": d2.content.get("pack_id"),
                        "publication_id": pub.publication_id,
                        "custom_pack_resolves": pk is not None,
                    },
                    ensure_ascii=False,
                    indent=2,
                )
            )
            return

        if with_assignment:
            lsvc = LearnerService(cfg, sessions)
            lid = f"smoke_learner_asg_{snapshot_id}".replace(" ", "_")[:80]
            try:
                lsvc.create_learner(lid, display_name="Smoke Assignment Learner")
            except ValueError:
                pass
            csvc = CurriculumService(cfg, sessions)
            pack = csvc.get_curriculum_pack(cfg.default_curriculum_pack_id)
            first_step = sorted(pack.steps, key=lambda x: x.order)[0].step_id if pack.steps else "step_foundation_01"
            asn = csvc.create_assignment(
                pack_id=pack.pack_id,
                learner_ids=[lid],
                created_by="smoke",
                title="Smoke curriculum assignment",
            )
            launch = csvc.launch_assignment_step_session(
                assignment_id=asn.assignment_id,
                pack_step_id=first_step,
                snapshot_id=snapshot_id,
                provider_name=provider,
                learner_id=lid,
            )
            sid = str(launch["session_id"])
            disc.submit_user_turn(sid, "Smoke assignment: user turn.")
            disc.run_next_turn(sid)
            disc.auto_run_discussion(sid, max_steps=2, auto_fill_user=True)
            report = fb.generate_feedback(sid)
            att = csvc.attach_session_to_assignment_step(
                assignment_id=asn.assignment_id,
                pack_step_id=first_step,
                session_id=sid,
            )
            rep = csvc.generate_assignment_report(asn.assignment_id)
            typer.echo(
                json.dumps(
                    {
                        "session_id": sid,
                        "assignment_id": asn.assignment_id,
                        "pack_step_id": first_step,
                        "learner_id": lid,
                        "coach_report": report.model_dump(),
                        "attach": att,
                        "assignment_report_id": rep.report_id,
                    },
                    ensure_ascii=False,
                    indent=2,
                )
            )
            return

        learner_id = None
        if with_learner:
            lsvc = LearnerService(cfg, sessions)
            lid = f"smoke_learner_{snapshot_id}".replace(" ", "_")[:80]
            try:
                lsvc.create_learner(lid, display_name="Smoke Learner")
            except ValueError:
                pass
            learner_id = lid
        ctx = sessions.create_session(
            snapshot_id=snapshot_id,
            topic_id=topic_id,
            user_stance=None,
            provider_name=provider,
            runtime_profile_id=runtime_profile,
            learner_id=learner_id,
            mode_id=mode_id,
            preset_id=("assessment_4p" if assessment_template_id else None),
            assessment_template_id=assessment_template_id,
            source="smoke",
        )
        root = Path(__file__).resolve().parents[3]
        if with_audio:
            wav = root / "tests" / "fixtures" / "audio" / "sample_user_turn_01.wav"
            audio = AudioService(cfg, sessions)
            audio.submit_user_audio_turn(ctx.session_id, wav, provider_name="mock_asr")
            disc.run_next_turn(ctx.session_id, with_tts=True, tts_provider="mock_tts")
        else:
            disc.submit_user_turn(ctx.session_id, "Smoke test: user turn.")
            disc.run_next_turn(ctx.session_id)
        disc.auto_run_discussion(ctx.session_id, max_steps=2, auto_fill_user=True)
        report = fb.generate_feedback(
            ctx.session_id,
            with_tts=with_audio,
            tts_provider="mock_tts" if with_audio else None,
            with_speech_analysis=with_speech_analysis and with_audio,
            speech_profile_id="speech_default" if (with_speech_analysis and with_audio) else None,
        )
        extra: dict = {"mode_id": ctx.mode_id, "assessment_template_id": ctx.assessment_template_id}
        if with_learner and learner_id:
            lsvc = LearnerService(cfg, sessions)
            try:
                lsvc.attach_session_to_learner(learner_id, ctx.session_id, ingest=True)
                recs = lsvc.get_recommendations(learner_id)
                extra = {
                    "learner_id": learner_id,
                    "recommendation_types": list({r.recommendation_type for r in recs}),
                }
            except Exception as e:
                extra = {"learner_id": learner_id, "learner_error": str(e)}
        review_extra: dict = {}
        if with_review:
            try:
                rsvc = ReviewService(cfg, sessions)
                rid = f"smoke_reviewer_{snapshot_id}".replace(" ", "_")[:80]
                try:
                    rsvc.create_reviewer(reviewer_id=rid, display_name="Smoke Reviewer")
                except ValueError:
                    pass
                pack = rsvc.create_review_pack(ctx.session_id)
                root = Path(__file__).resolve().parents[3]
                sample = root / "tests" / "fixtures" / "review" / "sample_manual_review.json"
                if sample.is_file():
                    import json as _json

                    payload = _json.loads(sample.read_text(encoding="utf-8"))
                    rsvc.submit_human_review(
                        review_pack_id=pack.review_pack_id,
                        reviewer_id=rid,
                        payload=payload,
                    )
                    cal = rsvc.compare_ai_vs_human(pack.review_pack_id)
                    review_extra = {
                        "review_pack_id": pack.review_pack_id,
                        "reviewer_id": rid,
                        "calibration_overall": cal.get("overall_agreement"),
                    }
            except Exception as e:
                review_extra = {"review_error": str(e)}
        fd_extra: dict = {}
        if final_delivery and release_profile:
            from app.ops.settings import get_ops_settings

            hs = HandoverService(cfg)
            ops = get_ops_settings()
            fd_extra["final_release_summary"] = hs.get_handover_summary(release_profile)
            fd_extra["delivery_verification"] = hs.verify_delivery(release_profile)
            fd_extra["release_manifest_built"] = bool(hs.build_release_manifest(release_profile).get("manifest"))
            demo_out = ops.demo_kit_dir / release_profile / "smoke_demo_kit"
            demo_out.mkdir(parents=True, exist_ok=True)
            fd_extra["demo_kit"] = hs.build_demo_kit(release_profile, demo_out)
            ho_out = ops.handover_kit_dir / release_profile / "smoke_kit"
            ho_out.mkdir(parents=True, exist_ok=True)
            fd_extra["handover_kit"] = hs.build_handover_kit(release_profile, ho_out)

        stability_extra: dict = {}
        if with_stability_audit and release_profile:
            st = StabilityService(cfg)
            stability_extra["stability_consistency_summary"] = st.run_consistency_audit(release_profile).get("summary")
            stability_extra["stability_overall"] = st.get_stability_report(
                release_profile, include_e2e=False
            ).get("overall_status")
            stability_extra["rc_go_no_go"] = st.build_rc_report(release_profile).get("go_no_go")
        typer.echo(
            json.dumps(
                {
                    "session_id": ctx.session_id,
                    "coach_report": report.model_dump(),
                    **extra,
                    **review_extra,
                    **release_extra,
                    **stability_extra,
                    **fd_extra,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
