"""Resolve built-in vs custom published authorable artifacts."""

from __future__ import annotations

import json
import uuid
from pathlib import Path
from typing import Any

from app.application.config import AppConfig
from app.authoring.constants import SRC_BUILTIN, SRC_CUSTOM_PUBLISHED, SRC_DERIVED
from app.integration_logging import warn_optional_hook_failed
from app.authoring.schemas.artifact import AuthorableArtifactRef
from app.curriculum.loaders.yaml_loader import list_builtin_pack_ids, load_builtin_pack
from app.curriculum.store.pack_store import PackStore
from app.group_sim.loaders.yaml_loader import get_roster_registry
from app.modes.loaders.yaml_loader import get_mode_registry
from app.runtime.profile_loader import list_profile_ids


def _ref(
    artifact_type: str,
    artifact_id: str,
    source_type: str,
    *,
    version: str | None = None,
    storage_ref: str | None = None,
    derivative_of: str | None = None,
    meta: dict[str, Any] | None = None,
) -> AuthorableArtifactRef:
    return AuthorableArtifactRef(
        artifact_ref_id=f"aref_{uuid.uuid4().hex[:10]}",
        artifact_type=artifact_type,
        artifact_id=artifact_id,
        source_type=source_type,
        version=version,
        storage_ref=storage_ref,
        derivative_of=derivative_of,
        metadata=meta or {},
    )


def list_authorable_artifacts(
    cfg: AppConfig,
    *,
    artifact_type: str | None = None,
    source_type: str | None = None,
    publication_store: Any | None = None,
) -> list[AuthorableArtifactRef]:
    """Enumerate builtin + custom published artifacts (minimal cross-subsystem)."""
    out: list[AuthorableArtifactRef] = []
    types = [artifact_type] if artifact_type else [
        "curriculum_pack",
        "runtime_profile",
        "scenario_preset",
        "assessment_template",
        "drill_spec",
        "roster_template",
        "topic_card",
        "pedagogy_item",
    ]

    ps = PackStore(cfg.curriculum_pack_builtin_dir, cfg.curriculum_custom_pack_dir)
    pubs = publication_store.list_publications() if publication_store else []

    for at in types:
        if at == "curriculum_pack":
            for pid in list_builtin_pack_ids():
                pk = load_builtin_pack(pid)
                out.append(
                    _ref(
                        "curriculum_pack",
                        pid,
                        SRC_BUILTIN,
                        version=getattr(pk, "version", None) if pk else None,
                        meta={"display_name": pk.display_name if pk else pid},
                    )
                )
            for f in sorted(cfg.curriculum_custom_pack_dir.glob("*.json")):
                try:
                    raw = json.loads(f.read_text(encoding="utf-8"))
                    pid = str(raw.get("pack_id") or f.stem)
                    out.append(
                        _ref(
                            "curriculum_pack",
                            pid,
                            SRC_CUSTOM_PUBLISHED,
                            storage_ref=str(f.relative_to(cfg.project_root)) if f.is_relative_to(cfg.project_root) else None,
                            meta={"source": "curriculum_custom_dir", "display_name": raw.get("display_name")},
                        )
                    )
                except Exception:
                    continue
            for pr in pubs:
                if pr.artifact_type == "curriculum_pack":
                    out.append(
                        _ref(
                            "curriculum_pack",
                            pr.artifact_id,
                            SRC_DERIVED,
                            version=pr.published_version,
                            storage_ref=pr.output_ref,
                            derivative_of=pr.derivative_of,
                            meta={"publication_id": pr.publication_id},
                        )
                    )

        elif at == "runtime_profile":
            for rid in list_profile_ids():
                out.append(_ref("runtime_profile", rid, SRC_BUILTIN, meta={}))
            pub_dir = cfg.authoring_published_runtime_profile_dir
            if pub_dir.is_dir():
                for f in sorted(pub_dir.glob("*.yaml")):
                    out.append(
                        _ref(
                            "runtime_profile",
                            f.stem,
                            SRC_CUSTOM_PUBLISHED,
                            storage_ref=str(f.name),
                            meta={},
                        )
                    )

        elif at in ("scenario_preset", "assessment_template", "drill_spec"):
            try:
                reg = get_mode_registry()
                if at == "scenario_preset":
                    for pid, pr in reg.presets.items():
                        out.append(_ref("scenario_preset", pid, SRC_BUILTIN, meta={"title": getattr(pr, "title", pid)}))
                elif at == "assessment_template":
                    for tid in reg.assessment_templates:
                        out.append(_ref("assessment_template", tid, SRC_BUILTIN, meta={}))
                elif at == "drill_spec":
                    for did in reg.drills:
                        out.append(_ref("drill_spec", did, SRC_BUILTIN, meta={}))
            except Exception as exc:
                warn_optional_hook_failed("authoring.resolve_mode_registry_builtins", exc, artifact_type=at)

        elif at == "roster_template":
            try:
                rreg = get_roster_registry()
                for tid in rreg.all_templates():
                    out.append(_ref("roster_template", tid, SRC_BUILTIN, meta={}))
            except Exception as exc:
                warn_optional_hook_failed("authoring.resolve_roster_registry_builtins", exc)

        elif at in ("topic_card", "pedagogy_item"):
            # Snapshot-backed discovery is optional; list published-only in phase 16
            for pr in pubs:
                if pr.artifact_type == at:
                    out.append(
                        _ref(
                            at,
                            pr.artifact_id,
                            SRC_CUSTOM_PUBLISHED,
                            version=pr.published_version,
                            storage_ref=pr.output_ref,
                            meta={"publication_id": pr.publication_id},
                        )
                    )

    if source_type:
        out = [a for a in out if a.source_type == source_type]
    return out


def load_base_content_for_derivative(
    cfg: AppConfig,
    artifact_type: str,
    artifact_id: str,
) -> dict[str, Any] | None:
    """Load base dict for derivative draft creation."""
    if artifact_type == "curriculum_pack":
        pk = load_builtin_pack(artifact_id)
        if pk:
            return pk.model_dump()
        p = cfg.curriculum_custom_pack_dir / f"{artifact_id}.json"
        if p.is_file():
            return json.loads(p.read_text(encoding="utf-8"))
    if artifact_type == "runtime_profile":
        from app.runtime.profile_loader import load_profile_yaml

        try:
            return load_profile_yaml(artifact_id)
        except FileNotFoundError:
            pub = cfg.authoring_published_runtime_profile_dir / f"{artifact_id}.yaml"
            if pub.is_file():
                import yaml

                raw = yaml.safe_load(pub.read_text(encoding="utf-8")) or {}
                return raw if isinstance(raw, dict) else {}
    return None
