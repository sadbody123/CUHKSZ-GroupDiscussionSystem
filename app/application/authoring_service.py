"""Authoring / curation / publication orchestration."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.application.config import AppConfig, get_app_config
from app.application.session_service import SessionService
from app.authoring.config import authoring_paths_from_app_config
from app.authoring.constants import DS_DRAFT, DS_PREVIEWED, DS_VALIDATED
from app.authoring.engines import artifact_resolver
from app.authoring.engines.diff_builder import build_diff, summarize_diff
from app.authoring.engines.lineage_tracker import build_lineage
from app.authoring.engines.patch_generator import (
    apply_ops_to_content,
    generate_patches_from_curriculum_gap,
    generate_patches_from_learner,
    generate_patches_from_review,
)
from app.authoring.engines.publisher import publish_draft as publish_engine
from app.authoring.engines.validator import run_validation
from app.authoring.pipeline.export_publication import export_publication_json
from app.authoring.pipeline.preview_draft import run_preview_draft
from app.authoring.pipeline.validate_draft import run_validate_draft
from app.authoring.schemas.artifact import AuthorableArtifactRef
from app.authoring.schemas.draft import AuthoringDraft
from app.authoring.schemas.patch import PatchProposal
from app.authoring.schemas.preview import PreviewResult
from app.authoring.schemas.publication import PublicationRecord
from app.authoring.schemas.validation import ValidationReport
from app.authoring.store import DraftStore, PatchStore, PublicationStore, rebuild_authoring_index


class AuthoringService:
    def __init__(
        self,
        config: AppConfig | None = None,
        session_service: SessionService | None = None,
    ) -> None:
        self._config = config or get_app_config()
        self._sessions = session_service or SessionService(self._config)
        self._paths = authoring_paths_from_app_config(self._config)
        self._drafts = DraftStore(self._paths.drafts_dir)
        self._patches = PatchStore(self._paths.patches_dir)
        self._publications = PublicationStore(
            self._paths.publications_dir,
            self._paths.published_root,
            project_root=self._config.project_root,
        )

    def _ensure(self) -> None:
        if not self._config.enable_authoring_studio:
            raise ValueError("authoring studio disabled")

    def _rebuild_index(self) -> None:
        rebuild_authoring_index(
            index_path=self._paths.index_path,
            drafts=self._drafts,
            patches=self._patches,
            publications=self._publications,
        )

    def list_authorable_artifacts(
        self,
        *,
        artifact_type: str | None = None,
        source_type: str | None = None,
    ) -> list[AuthorableArtifactRef]:
        self._ensure()
        return artifact_resolver.list_authorable_artifacts(
            self._config,
            artifact_type=artifact_type,
            source_type=source_type,
            publication_store=self._publications,
        )

    def create_derivative_draft(
        self,
        *,
        draft_id: str,
        artifact_type: str,
        base_artifact_id: str,
        author_id: str | None,
        title: str | None = None,
    ) -> AuthoringDraft:
        self._ensure()
        if not self._config.authoring_allow_derivative_from_builtin:
            raise ValueError("derivative drafts from built-in disabled")
        base = artifact_resolver.load_base_content_for_derivative(self._config, artifact_type, base_artifact_id)
        if not base:
            raise ValueError("base artifact not found")
        now = datetime.now(timezone.utc).isoformat()
        draft = AuthoringDraft(
            draft_id=draft_id,
            artifact_type=artifact_type,
            artifact_id=f"{base_artifact_id}_derivative",
            title=title or f"Derivative of {base_artifact_id}",
            author_id=author_id or self._config.default_author_id,
            base_artifact_ref_id=f"base:{artifact_type}:{base_artifact_id}",
            derivative_of=base_artifact_id,
            status=DS_DRAFT,
            created_at=now,
            updated_at=now,
            content=base,
            change_summary=["created as derivative"],
            metadata={
                "lineage": build_lineage(
                    base_artifact_ref_id=f"base:{artifact_type}:{base_artifact_id}",
                    derivative_of=base_artifact_id,
                    draft_id=draft_id,
                )
            },
        )
        if artifact_type == "curriculum_pack" and isinstance(base, dict):
            # Force new pack_id to avoid built-in collision on publish
            oid = str(base.get("pack_id") or base_artifact_id)
            draft.content = dict(base)
            draft.content["pack_id"] = f"{oid}_author_{draft_id[:8]}"
            draft.content.setdefault("metadata", {})
            draft.content["metadata"]["derivative_of"] = oid
        self._drafts.create_draft(draft)
        self._rebuild_index()
        return draft

    def create_blank_draft(
        self,
        *,
        draft_id: str,
        artifact_type: str,
        author_id: str | None,
        initial_content: dict | None = None,
        title: str | None = None,
    ) -> AuthoringDraft:
        self._ensure()
        now = datetime.now(timezone.utc).isoformat()
        aid = str((initial_content or {}).get("pack_id") or (initial_content or {}).get("topic_id") or draft_id)
        draft = AuthoringDraft(
            draft_id=draft_id,
            artifact_type=artifact_type,
            artifact_id=aid,
            title=title or draft_id,
            author_id=author_id or self._config.default_author_id,
            status=DS_DRAFT,
            created_at=now,
            updated_at=now,
            content=dict(initial_content or {}),
            change_summary=["blank draft"],
            metadata={},
        )
        self._drafts.create_draft(draft)
        self._rebuild_index()
        return draft

    def create_draft(
        self,
        *,
        draft_id: str,
        artifact_type: str,
        artifact_id: str | None,
        author_id: str | None,
        as_derivative: bool,
        initial_content: dict | None = None,
        title: str | None = None,
    ) -> AuthoringDraft:
        if as_derivative:
            if not artifact_id:
                raise ValueError("artifact_id required for derivative")
            return self.create_derivative_draft(
                draft_id=draft_id,
                artifact_type=artifact_type,
                base_artifact_id=artifact_id,
                author_id=author_id,
                title=title,
            )
        return self.create_blank_draft(
            draft_id=draft_id,
            artifact_type=artifact_type,
            author_id=author_id,
            initial_content=initial_content,
            title=title,
        )

    def list_drafts(self) -> list[AuthoringDraft]:
        self._ensure()
        return self._drafts.list_drafts()

    def get_draft(self, draft_id: str) -> AuthoringDraft:
        self._ensure()
        d = self._drafts.load_draft(draft_id)
        if not d:
            raise ValueError("draft not found")
        return d

    def validate_draft(self, draft_id: str) -> ValidationReport:
        self._ensure()
        draft = self.get_draft(draft_id)
        path = self._paths.validation_reports_dir / f"{draft_id}_validation.json"
        rep = run_validate_draft(draft, path)
        draft.status = DS_VALIDATED if rep.valid else draft.status
        draft.updated_at = datetime.now(timezone.utc).isoformat()
        self._drafts.save_draft(draft)
        self._rebuild_index()
        return rep

    def preview_draft(
        self,
        draft_id: str,
        *,
        preview_kind: str,
        snapshot_id: str | None = None,
        provider_name: str | None = "mock",
        learner_id: str | None = None,
    ) -> PreviewResult:
        self._ensure()
        if not self._config.enable_authoring_preview:
            raise ValueError("authoring preview disabled")
        draft = self.get_draft(draft_id)
        path = self._paths.preview_results_dir / f"{draft_id}_{preview_kind}.json"
        res = run_preview_draft(
            self._config,
            draft,
            preview_kind=preview_kind,
            snapshot_id=snapshot_id,
            provider_name=provider_name,
            learner_id=learner_id,
            result_path=path,
        )
        if res.success:
            draft.status = DS_PREVIEWED
            draft.updated_at = datetime.now(timezone.utc).isoformat()
            self._drafts.save_draft(draft)
        self._rebuild_index()
        return res

    def publish_draft(
        self,
        draft_id: str,
        *,
        published_version: str,
        published_by: str | None = None,
        validation_report_id: str | None = None,
        preview_result_ids: list[str] | None = None,
    ) -> PublicationRecord:
        self._ensure()
        draft = self.get_draft(draft_id)
        vr = run_validation(draft)
        if self._config.require_validation_before_publish and not vr.valid:
            raise ValueError("validation required before publish; fix findings or relax REQUIRE_VALIDATION_BEFORE_PUBLISH")
        if self._config.require_preview_before_publish and draft.status != DS_PREVIEWED:
            raise ValueError("preview required before publish")
        rec = publish_engine(
            self._config,
            draft,
            published_version=published_version,
            published_by=published_by or self._config.default_author_id,
            validation_report_id=validation_report_id or vr.report_id,
            preview_result_ids=list(preview_result_ids or []),
        )
        self._publications.save_publication_record(rec)
        draft.status = "published"
        draft.updated_at = datetime.now(timezone.utc).isoformat()
        self._drafts.save_draft(draft)
        self._rebuild_index()
        return rec

    def list_patch_proposals(self) -> list[PatchProposal]:
        self._ensure()
        return self._patches.list_patches()

    def generate_patch_proposals(
        self,
        *,
        source_type: str,
        source_id: str,
    ) -> list[PatchProposal]:
        self._ensure()
        patches: list[PatchProposal] = []
        if source_type == "review":
            patches = generate_patches_from_review(self._config, self._sessions, review_pack_id=source_id)
        elif source_type == "learner":
            patches = generate_patches_from_learner(self._config, self._sessions, learner_id=source_id)
        elif source_type == "curriculum":
            patches = generate_patches_from_curriculum_gap(assignment_id=source_id, completed_steps=0, total_steps=3)
        else:
            raise ValueError("unsupported source_type")
        for p in patches:
            self._patches.save_patch(p)
        self._rebuild_index()
        return patches

    def apply_patch_to_draft(self, draft_id: str, patch_id: str) -> AuthoringDraft:
        self._ensure()
        draft = self.get_draft(draft_id)
        patch = self._patches.load_patch(patch_id)
        if not patch:
            raise ValueError("patch not found")
        draft.content = apply_ops_to_content(draft.content, patch.proposed_ops)
        draft.linked_patch_ids.append(patch_id)
        draft.change_summary.append(f"applied patch {patch_id}")
        draft.updated_at = datetime.now(timezone.utc).isoformat()
        self._drafts.save_draft(draft)
        patch.status = "applied"
        self._patches.save_patch(patch)
        self._rebuild_index()
        return draft

    def list_publications(self, *, artifact_type: str | None = None) -> list[PublicationRecord]:
        self._ensure()
        return self._publications.list_publications(artifact_type=artifact_type)

    def get_publication(self, publication_id: str) -> PublicationRecord:
        self._ensure()
        r = self._publications.load_publication_record(publication_id)
        if not r:
            raise ValueError("publication not found")
        return r

    def export_published_artifact(self, publication_id: str, output_file: Path) -> Path:
        self._ensure()
        return export_publication_json(self._publications, publication_id, output_file)

    def diff_draft_vs_base(self, draft_id: str) -> dict[str, Any]:
        self._ensure()
        draft = self.get_draft(draft_id)
        if not draft.derivative_of:
            return {"changes": [], "summary": ["not a derivative draft"]}
        base = artifact_resolver.load_base_content_for_derivative(
            self._config, draft.artifact_type, draft.derivative_of
        )
        if not base:
            return {"changes": [], "summary": ["base not found"]}
        changes = build_diff(base, draft.content)
        return {"changes": changes, "summary": summarize_diff(changes)}
