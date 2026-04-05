"""Filesystem-backed artifact registry (passive scan)."""

from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any

import json

from app.ops.artifacts import paths as apaths
from app.ops.artifacts.inspectors import inspect_path
from app.ops.artifacts.manifests import snapshot_manifest
from app.ops.schemas import ArtifactRecord
from app.ops.settings import UnifiedSettings, get_ops_settings


class ArtifactRegistry:
    def __init__(self, settings: UnifiedSettings | None = None) -> None:
        self._s = settings or get_ops_settings()

    def scan_known_dirs(self) -> list[ArtifactRecord]:
        out: list[ArtifactRecord] = []
        root = apaths.snapshot_root(self._s)
        if root.is_dir():
            for child in sorted(root.iterdir()):
                if not child.is_dir():
                    continue
                rec = inspect_path(child)
                if rec and rec.artifact_kind == "snapshot":
                    out.append(rec)
        sdir = apaths.session_dir(self._s)
        if sdir.is_dir():
            for p in sorted(sdir.rglob("*.json")):
                rec = inspect_path(p)
                if rec:
                    out.append(rec)
        for d, kind_hint in (
            (apaths.eval_report_dir(self._s), "eval_report"),
            (apaths.feedback_report_dir(self._s), "feedback_report"),
        ):
            if not d.is_dir():
                continue
            for p in sorted(d.rglob("*.json")):
                rec = inspect_path(p)
                if rec:
                    if kind_hint and rec.artifact_kind != kind_hint:
                        rec = rec.model_copy(update={"artifact_kind": kind_hint})
                    out.append(rec)
        bdir = apaths.bundle_dir(self._s)
        if bdir.is_dir():
            for p in sorted(bdir.glob("*.zip")):
                rec = inspect_path(p)
                if rec:
                    out.append(rec)
        aman = apaths.audio_storage_dir(self._s) / "_manifests"
        if aman.is_dir():
            for p in sorted(aman.glob("*.json")):
                try:
                    raw = json.loads(p.read_text(encoding="utf-8"))
                    aid = str(raw.get("asset_id") or p.stem)
                except (OSError, json.JSONDecodeError, TypeError):
                    aid = p.stem
                out.append(
                    ArtifactRecord(
                        artifact_id=aid,
                        artifact_kind="audio_asset",
                        path=str(p.resolve()),
                        created_at="",
                        size_bytes=p.stat().st_size if p.is_file() else None,
                        metadata={"manifest": True},
                    )
                )
        sdir = apaths.speech_report_dir(self._s)
        if sdir.is_dir():
            for p in sorted(sdir.rglob("*.json")):
                try:
                    raw = json.loads(p.read_text(encoding="utf-8"))
                    rid = str(raw.get("report_id") or raw.get("analysis_id") or p.stem)
                except (OSError, json.JSONDecodeError, TypeError):
                    rid = p.stem
                out.append(
                    ArtifactRecord(
                        artifact_id=rid,
                        artifact_kind="speech_analysis_report",
                        path=str(p.resolve()),
                        created_at="",
                        size_bytes=p.stat().st_size if p.is_file() else None,
                        metadata={"speech_report": True},
                    )
                )
        ldir = apaths.learner_dir(self._s)
        if ldir.is_dir():
            for p in sorted(ldir.rglob("*.json")):
                rec = inspect_path(p)
                if rec:
                    out.append(rec)
        mdir = apaths.mode_reports_dir(self._s)
        if mdir.is_dir():
            for p in sorted(mdir.glob("*.json")):
                rec = inspect_path(p)
                if rec:
                    out.append(rec)
        gdir = apaths.group_reports_dir(self._s)
        if gdir.is_dir():
            for p in sorted(gdir.glob("*.json")):
                rec = inspect_path(p)
                if rec:
                    out.append(rec)
        rdir = apaths.reviewer_storage_dir(self._s)
        if rdir.is_dir():
            for p in sorted(rdir.glob("*.json")):
                out.append(
                    ArtifactRecord(
                        artifact_id=p.stem,
                        artifact_kind="reviewer_profile",
                        path=str(p.resolve()),
                        created_at="",
                        size_bytes=p.stat().st_size if p.is_file() else None,
                        metadata={},
                    )
                )
        cdir = apaths.curriculum_custom_pack_dir(self._s)
        if cdir.is_dir():
            for p in sorted(cdir.glob("*.json")):
                out.append(
                    ArtifactRecord(
                        artifact_id=p.stem,
                        artifact_kind="curriculum_pack",
                        path=str(p.resolve()),
                        created_at="",
                        size_bytes=p.stat().st_size if p.is_file() else None,
                        metadata={"custom": True},
                    )
                )
        adir = apaths.assignment_storage_dir(self._s)
        if adir.is_dir():
            for child in sorted(adir.iterdir()):
                if not child.is_dir():
                    continue
                for name, kind in (("spec.json", "assignment"), ("report.json", "assignment_report")):
                    p = child / name
                    if p.is_file():
                        out.append(
                            ArtifactRecord(
                                artifact_id=child.name,
                                artifact_kind=kind,
                                path=str(p.resolve()),
                                created_at="",
                                size_bytes=p.stat().st_size,
                                metadata={},
                            )
                        )
                att = child / "attempts.jsonl"
                if att.is_file():
                    out.append(
                        ArtifactRecord(
                            artifact_id=f"{child.name}_attempts",
                            artifact_kind="assignment_attempt",
                            path=str(att.resolve()),
                            created_at="",
                            size_bytes=att.stat().st_size,
                            metadata={},
                        )
                    )
        revdir = apaths.review_storage_dir(self._s)
        if revdir.is_dir():
            for sub, kind in (
                ("review_packs", "review_pack"),
                ("submissions", "human_review"),
                ("calibration", "calibration_report"),
                ("reviewed_outputs", "reviewed_feedback"),
            ):
                d = revdir / sub
                if not d.is_dir():
                    continue
                for p in sorted(d.glob("*.json")):
                    out.append(
                        ArtifactRecord(
                            artifact_id=p.stem,
                            artifact_kind=kind,
                            path=str(p.resolve()),
                            created_at="",
                            size_bytes=p.stat().st_size if p.is_file() else None,
                            metadata={},
                        )
                    )
        rel_rep = getattr(self._s, "release_report_dir", None)
        if rel_rep and Path(rel_rep).is_dir():
            for p in sorted(Path(rel_rep).glob("*.json")):
                stem = p.stem.lower()
                if "capability_matrix" in stem:
                    kind = "capability_matrix"
                elif "scope" in stem or "freeze" in stem:
                    kind = "scope_freeze_report"
                elif "readiness" in stem:
                    kind = "readiness_report"
                else:
                    kind = "readiness_report"
                out.append(
                    ArtifactRecord(
                        artifact_id=p.stem,
                        artifact_kind=kind,
                        path=str(p.resolve()),
                        created_at="",
                        size_bytes=p.stat().st_size if p.is_file() else None,
                        metadata={"release": True},
                    )
                )
        rprof = getattr(self._s, "release_profile_dir", None)
        if rprof and Path(rprof).is_dir():
            for p in sorted(Path(rprof).glob("*.yaml")):
                out.append(
                    ArtifactRecord(
                        artifact_id=p.stem,
                        artifact_kind="release_profile",
                        path=str(p.resolve()),
                        created_at="",
                        size_bytes=p.stat().st_size if p.is_file() else None,
                        metadata={"release": True},
                    )
                )
        dbun = getattr(self._s, "demo_bundle_dir", None)
        if dbun and Path(dbun).is_dir():
            for p in sorted(Path(dbun).rglob("manifest.json")):
                out.append(
                    ArtifactRecord(
                        artifact_id=p.parent.name,
                        artifact_kind="demo_bundle",
                        path=str(p.resolve()),
                        created_at="",
                        size_bytes=p.stat().st_size if p.is_file() else None,
                        metadata={"release": True},
                    )
                )
            for p in sorted(Path(dbun).rglob("scenario_results/*.json")):
                out.append(
                    ArtifactRecord(
                        artifact_id=f"{p.parent.parent.name}_{p.stem}",
                        artifact_kind="demo_scenario_result",
                        path=str(p.resolve()),
                        created_at="",
                        size_bytes=p.stat().st_size if p.is_file() else None,
                        metadata={"release": True},
                    )
                )

        stab_root = getattr(self._s, "stability_report_dir", None)
        if stab_root and Path(stab_root).is_dir():
            for p in sorted(Path(stab_root).glob("*.json")):
                kind = "stability_report" if "stability" in p.name.lower() else "stability_report"
                out.append(
                    ArtifactRecord(
                        artifact_id=p.stem,
                        artifact_kind=kind,
                        path=str(p.resolve()),
                        created_at="",
                        size_bytes=p.stat().st_size if p.is_file() else None,
                        metadata={"stability": True},
                    )
                )
        cr = getattr(self._s, "consistency_report_dir", None)
        if cr and Path(cr).is_dir():
            for p in sorted(Path(cr).glob("*.json")):
                out.append(
                    ArtifactRecord(
                        artifact_id=p.stem,
                        artifact_kind="consistency_report",
                        path=str(p.resolve()),
                        created_at="",
                        size_bytes=p.stat().st_size if p.is_file() else None,
                        metadata={"stability": True},
                    )
                )
        e2e = getattr(self._s, "e2e_results_dir", None)
        if e2e and Path(e2e).is_dir():
            for p in sorted(Path(e2e).glob("*.json")):
                out.append(
                    ArtifactRecord(
                        artifact_id=p.stem,
                        artifact_kind="e2e_run_result",
                        path=str(p.resolve()),
                        created_at="",
                        size_bytes=p.stat().st_size if p.is_file() else None,
                        metadata={"stability": True},
                    )
                )
        rc = getattr(self._s, "rc_report_dir", None)
        if rc and Path(rc).is_dir():
            for p in sorted(Path(rc).glob("*.json")):
                out.append(
                    ArtifactRecord(
                        artifact_id=p.stem,
                        artifact_kind="rc_report",
                        path=str(p.resolve()),
                        created_at="",
                        size_bytes=p.stat().st_size if p.is_file() else None,
                        metadata={"stability": True},
                    )
                )
        kid = getattr(self._s, "known_issues_dir", None)
        if kid and Path(kid).is_dir():
            for p in sorted(Path(kid).glob("*.yaml")):
                out.append(
                    ArtifactRecord(
                        artifact_id=p.stem,
                        artifact_kind="known_limitations_manifest",
                        path=str(p.resolve()),
                        created_at="",
                        size_bytes=p.stat().st_size if p.is_file() else None,
                        metadata={"stability": True},
                    )
                )
            sub = Path(kid) / "issues"
            if sub.is_dir():
                for p in sorted(sub.glob("*.yaml")):
                    out.append(
                        ArtifactRecord(
                            artifact_id=p.stem,
                            artifact_kind="issue_record",
                            path=str(p.resolve()),
                            created_at="",
                            size_bytes=p.stat().st_size if p.is_file() else None,
                            metadata={"stability": True},
                        )
                    )

        rmd = getattr(self._s, "release_manifest_dir", None)
        if rmd and Path(rmd).is_dir():
            for p in sorted(Path(rmd).glob("*.json")):
                out.append(
                    ArtifactRecord(
                        artifact_id=p.stem,
                        artifact_kind="final_release_manifest",
                        path=str(p.resolve()),
                        created_at="",
                        size_bytes=p.stat().st_size if p.is_file() else None,
                        metadata={"handover": True},
                    )
                )
        bomd = getattr(self._s, "bom_dir", None)
        if bomd and Path(bomd).is_dir():
            for p in sorted(Path(bomd).glob("*_bom.json")):
                out.append(
                    ArtifactRecord(
                        artifact_id=p.stem,
                        artifact_kind="bill_of_materials",
                        path=str(p.resolve()),
                        created_at="",
                        size_bytes=p.stat().st_size if p.is_file() else None,
                        metadata={"handover": True},
                    )
                )
        dkd = getattr(self._s, "demo_kit_dir", None)
        if dkd and Path(dkd).is_dir():
            for p in sorted(Path(dkd).rglob("demo_kit_manifest.json")):
                out.append(
                    ArtifactRecord(
                        artifact_id=p.parent.name,
                        artifact_kind="demo_kit",
                        path=str(p.resolve()),
                        created_at="",
                        size_bytes=p.stat().st_size if p.is_file() else None,
                        metadata={"handover": True},
                    )
                )
        hkd = getattr(self._s, "handover_kit_dir", None)
        if hkd and Path(hkd).is_dir():
            for p in sorted(Path(hkd).rglob("handover_kit_manifest.json")):
                out.append(
                    ArtifactRecord(
                        artifact_id=p.parent.name,
                        artifact_kind="handover_kit",
                        path=str(p.resolve()),
                        created_at="",
                        size_bytes=p.stat().st_size if p.is_file() else None,
                        metadata={"handover": True},
                    )
                )
        aed = getattr(self._s, "acceptance_evidence_dir", None)
        if aed and Path(aed).is_dir():
            for p in sorted(Path(aed).glob("*_acceptance_evidence.json")):
                out.append(
                    ArtifactRecord(
                        artifact_id=p.stem,
                        artifact_kind="acceptance_evidence",
                        path=str(p.resolve()),
                        created_at="",
                        size_bytes=p.stat().st_size if p.is_file() else None,
                        metadata={"handover": True},
                    )
                )
        dvd = getattr(self._s, "delivery_verification_dir", None)
        if dvd and Path(dvd).is_dir():
            for p in sorted(Path(dvd).glob("*.json")):
                out.append(
                    ArtifactRecord(
                        artifact_id=p.stem,
                        artifact_kind="delivery_verification_report",
                        path=str(p.resolve()),
                        created_at="",
                        size_bytes=p.stat().st_size if p.is_file() else None,
                        metadata={"handover": True},
                    )
                )
        fdd = getattr(self._s, "final_docs_bundle_dir", None)
        if fdd and Path(fdd).is_dir():
            for p in sorted(Path(fdd).rglob("*.md")):
                out.append(
                    ArtifactRecord(
                        artifact_id=p.stem,
                        artifact_kind="docs_bundle",
                        path=str(p.resolve()),
                        created_at="",
                        size_bytes=p.stat().st_size if p.is_file() else None,
                        metadata={"handover": True},
                    )
                )
        frd = getattr(self._s, "final_release_dir", None)
        if frd and Path(frd).is_dir():
            for p in sorted(Path(frd).glob("*.zip")):
                out.append(
                    ArtifactRecord(
                        artifact_id=p.stem,
                        artifact_kind="final_release_package",
                        path=str(p.resolve()),
                        created_at="",
                        size_bytes=p.stat().st_size if p.is_file() else None,
                        metadata={"handover": True},
                    )
                )

        auth_root = getattr(self._s, "authoring_root_dir", None)
        if auth_root and Path(auth_root).is_dir():
            aroot = Path(auth_root).resolve()
            for sub, kind in (
                ("drafts", "authoring_draft"),
                ("patches", "patch_proposal"),
                ("publications", "publication_record"),
                ("validation_reports", "validation_report"),
                ("preview_results", "preview_result"),
            ):
                d = aroot / sub
                if not d.is_dir():
                    continue
                for p in sorted(d.glob("*.json")):
                    out.append(
                        ArtifactRecord(
                            artifact_id=p.stem,
                            artifact_kind=kind,
                            path=str(p.resolve()),
                            created_at="",
                            size_bytes=p.stat().st_size if p.is_file() else None,
                            metadata={"authoring": True},
                        )
                    )
        return out

    def list_artifacts(self, kind: str | None = None) -> list[ArtifactRecord]:
        rows = self.scan_known_dirs()
        if kind:
            rows = [r for r in rows if r.artifact_kind == kind]
        return rows

    def inspect_artifact(self, *, artifact_id: str | None = None, path: str | None = None) -> ArtifactRecord | None:
        if path:
            return inspect_path(Path(path))
        if not artifact_id:
            return None
        for r in self.scan_known_dirs():
            if r.artifact_id == artifact_id:
                return r
        snap = apaths.snapshot_root(self._s) / artifact_id
        if snap.is_dir():
            return inspect_path(snap)
        return None

    def register_artifact(self, path: Path, kind: str, metadata: dict[str, Any] | None = None) -> ArtifactRecord:
        rec = inspect_path(path)
        if not rec:
            rec = ArtifactRecord(
                artifact_id=path.stem,
                artifact_kind=kind,
                path=str(path.resolve()),
                created_at="",
                size_bytes=None,
                metadata={},
            )
        else:
            rec = rec.model_copy(update={"artifact_kind": kind, "metadata": {**(rec.metadata or {}), **(metadata or {})}})
        return rec

    def summarize_by_kind(self) -> dict[str, int]:
        c = Counter()
        for r in self.scan_known_dirs():
            c[r.artifact_kind] += 1
        return dict(c)


def snapshot_ids_under_root(settings: UnifiedSettings | None = None) -> list[str]:
    s = settings or get_ops_settings()
    root = apaths.snapshot_root(s)
    if not root.is_dir():
        return []
    out: list[str] = []
    for child in sorted(root.iterdir()):
        if not child.is_dir():
            continue
        mf = snapshot_manifest(child)
        if mf is not None:
            out.append(child.name)
    return out
