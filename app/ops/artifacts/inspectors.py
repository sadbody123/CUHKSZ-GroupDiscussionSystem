"""Inspect a path and infer artifact kind + metadata."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.ops.artifacts.manifests import snapshot_manifest
from app.ops.schemas import ArtifactRecord


def _iso_mtime(p: Path) -> str:
    try:
        ts = p.stat().st_mtime
        return datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()
    except OSError:
        return ""


def _size(p: Path) -> int | None:
    try:
        return p.stat().st_size if p.is_file() else None
    except OSError:
        return None


def inspect_path(path: Path) -> ArtifactRecord | None:
    p = path.resolve()
    if not p.exists():
        return None
    if p.is_file() and p.suffix.lower() == ".zip":
        return ArtifactRecord(
            artifact_id=p.stem,
            artifact_kind="snapshot_bundle",
            path=str(p),
            created_at=_iso_mtime(p),
            size_bytes=_size(p),
            metadata={"filename": p.name},
        )
    if p.is_file() and p.suffix.lower() == ".json":
        rel = str(p).lower()
        kind = "session"
        if "group_reports" in rel and p.suffix.lower() == ".json":
            kind = "group_balance_report"
        elif "mode_reports" in rel and p.suffix.lower() == ".json":
            kind = "mode_report"
        elif "learners" in rel:
            if p.name.lower() == "profile.json":
                kind = "learner_profile"
            elif "\\reports\\" in rel or "/reports/" in rel:
                kind = "learner_report"
            elif "\\plans\\" in rel or "/plans/" in rel:
                kind = "learning_plan"
            else:
                kind = "learner_artifact"
        elif "eval" in rel:
            kind = "eval_report"
        elif "storage\\reviews" in rel or "storage/reviews" in rel:
            if "review_packs" in rel:
                kind = "review_pack"
            elif "submissions" in rel:
                kind = "human_review"
            elif "calibration" in rel:
                kind = "calibration_report"
            elif "reviewed_outputs" in rel:
                kind = "reviewed_feedback"
            else:
                kind = "review_artifact"
        elif "storage\\reviewers" in rel or "storage/reviewers" in rel:
            kind = "reviewer_profile"
        elif "feedback" in rel:
            kind = "feedback_report"
        meta: dict[str, Any] = {}
        try:
            raw = json.loads(p.read_text(encoding="utf-8"))
            if isinstance(raw, dict):
                meta["keys"] = list(raw.keys())[:20]
        except (OSError, json.JSONDecodeError):
            pass
        aid = p.stem
        return ArtifactRecord(
            artifact_id=aid,
            artifact_kind=kind,
            path=str(p),
            created_at=_iso_mtime(p),
            size_bytes=_size(p),
            metadata=meta,
        )
    if p.is_dir() and (p / "manifest.json").is_file():
        mf = snapshot_manifest(p) or {}
        sid = str(mf.get("snapshot_id") or p.name)
        return ArtifactRecord(
            artifact_id=sid,
            artifact_kind="snapshot",
            path=str(p),
            created_at=str(mf.get("created_at") or _iso_mtime(p / "manifest.json")),
            size_bytes=None,
            metadata={"schema_version": str(mf.get("schema_version", "")), "folder": p.name},
        )
    return None
