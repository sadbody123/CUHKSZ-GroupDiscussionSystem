"""HTTP client for FastAPI backend (Streamlit and tools)."""

from __future__ import annotations

from typing import Any

import httpx


class ApiError(Exception):
    def __init__(self, message: str, *, status_code: int | None = None, body: Any = None) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.body = body


class DiscussionApiClient:
    def __init__(self, base_url: str, *, timeout: float = 120.0) -> None:
        self._base = base_url.rstrip("/")
        self._timeout = timeout

    def _url(self, path: str) -> str:
        return f"{self._base}{path}" if path.startswith("/") else f"{self._base}/{path}"

    def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: Any | None = None,
    ) -> Any:
        try:
            with httpx.Client(timeout=self._timeout) as client:
                r = client.request(method, self._url(path), params=params, json=json)
        except httpx.RequestError as e:
            raise ApiError(f"HTTP request failed: {e}") from e
        if r.status_code >= 400:
            try:
                body = r.json()
            except Exception:
                body = r.text
            raise ApiError(
                f"API error {r.status_code}",
                status_code=r.status_code,
                body=body,
            )
        if r.status_code == 204 or not r.content:
            return None
        return r.json()

    def _post_multipart(
        self,
        path: str,
        *,
        files: dict[str, Any],
        data: dict[str, Any] | None = None,
    ) -> Any:
        try:
            with httpx.Client(timeout=self._timeout) as client:
                r = client.post(self._url(path), files=files, data=data or {})
        except httpx.RequestError as e:
            raise ApiError(f"HTTP request failed: {e}") from e
        if r.status_code >= 400:
            try:
                body = r.json()
            except Exception:
                body = r.text
            raise ApiError(f"API error {r.status_code}", status_code=r.status_code, body=body)
        return r.json()

    def get_health(self) -> dict[str, Any]:
        return self._request("GET", "/health")

    def get_system_info(self) -> dict[str, Any]:
        return self._request("GET", "/system/info")

    def get_system_capabilities(self) -> list[dict[str, Any]]:
        data = self._request("GET", "/system/capabilities")
        return (data or {}).get("capabilities") or []

    def get_active_release_profile(self, profile_id: str | None = None) -> dict[str, Any]:
        params = {"profile_id": profile_id} if profile_id else None
        data = self._request("GET", "/system/release-profile", params=params)
        return (data or {}).get("profile") or {}

    def list_release_profiles(self) -> list[str]:
        return self._request("GET", "/system/release-profiles") or []

    def get_system_readiness(self, profile_id: str | None = None) -> dict[str, Any]:
        params = {"profile_id": profile_id} if profile_id else None
        data = self._request("GET", "/system/readiness", params=params)
        return (data or {}).get("report") or {}

    def run_system_demo_scenario(
        self,
        scenario_id: str,
        *,
        profile_id: str | None = None,
        snapshot_id: str = "dev_snapshot_v2",
        topic_id: str = "tc-campus-ai",
        provider_name: str = "mock",
    ) -> dict[str, Any]:
        payload = {
            "profile_id": profile_id,
            "snapshot_id": snapshot_id,
            "topic_id": topic_id,
            "provider_name": provider_name,
        }
        data = self._request("POST", f"/system/demo-scenarios/{scenario_id}/run", json=payload)
        return (data or {}).get("result") or {}

    def get_scope_freeze_summary(self, profile_id: str | None = None) -> dict[str, Any]:
        params = {"profile_id": profile_id} if profile_id else None
        data = self._request("GET", "/system/scope-freeze", params=params)
        return (data or {}).get("summary") or {}

    def get_release_visibility(self, profile_id: str | None = None) -> dict[str, Any]:
        params = {"profile_id": profile_id} if profile_id else None
        data = self._request("GET", "/system/release-visibility", params=params)
        return (data or {}).get("state") or {}

    def list_e2e_scenarios(self) -> list[dict[str, Any]]:
        data = self._request("GET", "/system/e2e-scenarios")
        return (data or {}).get("scenarios") or []

    def get_e2e_scenario_detail(self, scenario_id: str) -> dict[str, Any]:
        data = self._request("GET", f"/system/e2e-scenarios/{scenario_id}")
        return (data or {}).get("scenario") or {}

    def run_e2e_scenario(
        self,
        scenario_id: str,
        *,
        profile_id: str | None = None,
        snapshot_id: str = "dev_snapshot_v2",
        topic_id: str = "tc-campus-ai",
        provider_name: str = "mock",
    ) -> dict[str, Any]:
        params = {
            "snapshot_id": snapshot_id,
            "topic_id": topic_id,
            "provider_name": provider_name,
        }
        if profile_id:
            params["profile_id"] = profile_id
        data = self._request("POST", f"/system/e2e-scenarios/{scenario_id}/run", params=params)
        return (data or {}).get("result") or {}

    def get_consistency_summary(self, profile_id: str | None = None) -> dict[str, Any]:
        params = {"profile_id": profile_id} if profile_id else None
        data = self._request("GET", "/system/consistency", params=params)
        return (data or {}).get("summary") or {}

    def get_stability_report(
        self,
        profile_id: str | None = None,
        *,
        include_e2e: bool = False,
    ) -> dict[str, Any]:
        params: dict[str, Any] = {"include_e2e": include_e2e}
        if profile_id:
            params["profile_id"] = profile_id
        data = self._request("GET", "/system/stability", params=params)
        return (data or {}).get("report") or {}

    def list_known_issues(self) -> list[dict[str, Any]]:
        data = self._request("GET", "/system/known-issues")
        return (data or {}).get("issues") or []

    def get_release_candidate_report(self, profile_id: str | None = None) -> dict[str, Any]:
        params = {"profile_id": profile_id} if profile_id else None
        data = self._request("GET", "/system/release-candidate", params=params)
        return (data or {}).get("report") or {}

    def get_release_manifest_summary(self, profile_id: str | None = None) -> dict[str, Any]:
        params = {"profile_id": profile_id} if profile_id else None
        data = self._request("GET", "/system/release-manifest", params=params)
        return (data or {}).get("manifest") or {}

    def get_bom_summary(self, profile_id: str | None = None) -> dict[str, Any]:
        params = {"profile_id": profile_id} if profile_id else None
        return self._request("GET", "/system/bom", params=params) or {}

    def get_demo_kit_summary(self, profile_id: str | None = None) -> dict[str, Any]:
        params = {"profile_id": profile_id} if profile_id else None
        return self._request("GET", "/system/demo-kit", params=params) or {}

    def get_acceptance_evidence(self, profile_id: str | None = None) -> dict[str, Any]:
        params = {"profile_id": profile_id} if profile_id else None
        data = self._request("GET", "/system/acceptance", params=params)
        return (data or {}).get("evidence") or {}

    def post_verify_delivery(self, profile_id: str | None = None) -> dict[str, Any]:
        params = {"profile_id": profile_id} if profile_id else None
        data = self._request("POST", "/system/verify-delivery", params=params)
        return (data or {}).get("report") or {}

    def get_handover_kit_summary(self, profile_id: str | None = None) -> dict[str, Any]:
        params = {"profile_id": profile_id} if profile_id else None
        return self._request("GET", "/system/handover-kit", params=params) or {}

    def get_final_release_summary(self, profile_id: str | None = None) -> dict[str, Any]:
        params = {"profile_id": profile_id} if profile_id else None
        data = self._request("GET", "/system/final-release-summary", params=params)
        return (data or {}).get("summary") or {}

    def list_snapshots(self) -> list[dict[str, Any]]:
        return self._request("GET", "/snapshots")

    def get_snapshot(self, snapshot_id: str) -> dict[str, Any]:
        return self._request("GET", f"/snapshots/{snapshot_id}")

    def get_index_status(self, snapshot_id: str) -> dict[str, Any]:
        return self._request("GET", f"/snapshots/{snapshot_id}/index-status")

    def list_topics(self, snapshot_id: str, keyword: str | None = None) -> list[dict[str, Any]]:
        params: dict[str, Any] = {"snapshot_id": snapshot_id}
        if keyword:
            params["keyword"] = keyword
        return self._request("GET", "/topics", params=params)

    def get_topic(self, snapshot_id: str, topic_id: str) -> dict[str, Any]:
        return self._request("GET", f"/topics/{topic_id}", params={"snapshot_id": snapshot_id})

    def list_profiles(self) -> list[dict[str, Any]]:
        return self._request("GET", "/profiles")

    def get_profile(self, profile_id: str) -> dict[str, Any]:
        return self._request("GET", f"/profiles/{profile_id}")

    def create_session(
        self,
        *,
        snapshot_id: str,
        topic_id: str,
        user_stance: str | None,
        provider_name: str = "mock",
        model_name: str | None = None,
        max_discussion_turns: int | None = None,
        runtime_profile_id: str | None = None,
        learner_id: str | None = None,
        mode_id: str | None = None,
        preset_id: str | None = None,
        drill_id: str | None = None,
        assessment_template_id: str | None = None,
        roster_template_id: str | None = None,
        user_participant_id: str | None = None,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "snapshot_id": snapshot_id,
            "topic_id": topic_id,
            "user_stance": user_stance,
            "provider_name": provider_name,
        }
        if model_name is not None:
            payload["model_name"] = model_name
        if max_discussion_turns is not None:
            payload["max_discussion_turns"] = max_discussion_turns
        if runtime_profile_id is not None:
            payload["runtime_profile_id"] = runtime_profile_id
        if learner_id is not None:
            payload["learner_id"] = learner_id
        if mode_id is not None:
            payload["mode_id"] = mode_id
        if preset_id is not None:
            payload["preset_id"] = preset_id
        if drill_id is not None:
            payload["drill_id"] = drill_id
        if assessment_template_id is not None:
            payload["assessment_template_id"] = assessment_template_id
        if roster_template_id is not None:
            payload["roster_template_id"] = roster_template_id
        if user_participant_id is not None:
            payload["user_participant_id"] = user_participant_id
        return self._request("POST", "/sessions", json=payload)

    def list_sessions(self) -> list[dict[str, Any]]:
        return self._request("GET", "/sessions")

    def get_session(self, session_id: str) -> dict[str, Any]:
        return self._request("GET", f"/sessions/{session_id}")

    def submit_user_turn(self, session_id: str, text: str) -> dict[str, Any]:
        return self._request("POST", f"/sessions/{session_id}/turns/user", json={"text": text})

    def run_next_turn(
        self,
        session_id: str,
        *,
        with_tts: bool = False,
        tts_provider: str | None = None,
    ) -> dict[str, Any]:
        params: dict[str, Any] = {}
        if with_tts:
            params["with_tts"] = True
        if tts_provider:
            params["tts_provider"] = tts_provider
        return self._request("POST", f"/sessions/{session_id}/run-next", params=params or None)

    def auto_run(self, session_id: str, max_steps: int) -> dict[str, Any]:
        return self._request("POST", f"/sessions/{session_id}/auto-run", json={"max_steps": max_steps})

    def generate_feedback(
        self,
        session_id: str,
        *,
        with_tts: bool = False,
        tts_provider: str | None = None,
        with_speech_analysis: bool = False,
        speech_profile_id: str | None = None,
    ) -> dict[str, Any]:
        params: dict[str, Any] = {}
        if with_tts:
            params["with_tts"] = True
        if tts_provider:
            params["tts_provider"] = tts_provider
        if with_speech_analysis:
            params["with_speech_analysis"] = True
        if speech_profile_id:
            params["speech_profile_id"] = speech_profile_id
        return self._request("POST", f"/sessions/{session_id}/feedback", params=params or None)

    def export_session(self, session_id: str) -> dict[str, Any]:
        return self._request("GET", f"/sessions/{session_id}/export")

    def user_transcribe_audio(
        self,
        session_id: str,
        file_bytes: bytes,
        filename: str,
        *,
        save_asset: bool = False,
        provider_name: str | None = None,
    ) -> dict[str, Any]:
        files = {"audio": (filename, file_bytes, "audio/wav")}
        data: dict[str, Any] = {"save_asset": "true" if save_asset else "false"}
        if provider_name:
            data["provider_name"] = provider_name
        return self._post_multipart(f"/sessions/{session_id}/audio/user-transcribe", files=files, data=data)

    def user_submit_audio(
        self,
        session_id: str,
        file_bytes: bytes,
        filename: str,
        *,
        provider_name: str | None = None,
    ) -> dict[str, Any]:
        files = {"audio": (filename, file_bytes, "audio/wav")}
        data: dict[str, Any] = {}
        if provider_name:
            data["provider_name"] = provider_name
        return self._post_multipart(f"/sessions/{session_id}/audio/user-submit", files=files, data=data)

    def list_session_audio_assets(self, session_id: str) -> dict[str, Any]:
        return self._request("GET", f"/sessions/{session_id}/audio-assets")

    def synthesize_turn_tts(self, session_id: str, turn_id: str, *, provider_name: str | None = None) -> dict[str, Any]:
        params: dict[str, Any] = {}
        if provider_name:
            params["provider_name"] = provider_name
        return self._request(
            "POST",
            f"/sessions/{session_id}/turns/{turn_id}/tts",
            params=params or None,
        )

    def fetch_audio_bytes(self, asset_id: str) -> tuple[bytes, str]:
        try:
            with httpx.Client(timeout=self._timeout) as client:
                r = client.get(self._url(f"/audio/{asset_id}"))
        except httpx.RequestError as e:
            raise ApiError(f"HTTP request failed: {e}") from e
        if r.status_code >= 400:
            raise ApiError(f"API error {r.status_code}", status_code=r.status_code, body=r.text)
        mime = r.headers.get("content-type", "audio/wav")
        return r.content, mime

    def analyze_turn_speech(
        self, session_id: str, turn_id: str, *, profile_id: str | None = None
    ) -> dict[str, Any]:
        params: dict[str, Any] = {}
        if profile_id:
            params["profile_id"] = profile_id
        return self._request(
            "POST",
            f"/sessions/{session_id}/turns/{turn_id}/speech/analyze",
            params=params or None,
        )

    def analyze_session_speech(self, session_id: str, *, profile_id: str | None = None) -> dict[str, Any]:
        params: dict[str, Any] = {}
        if profile_id:
            params["profile_id"] = profile_id
        return self._request("POST", f"/sessions/{session_id}/speech/analyze", params=params or None)

    def get_speech_report(self, session_id: str) -> dict[str, Any]:
        return self._request("GET", f"/sessions/{session_id}/speech-report")

    def create_learner(self, learner_id: str, display_name: str | None = None) -> dict[str, Any]:
        payload: dict[str, Any] = {"learner_id": learner_id}
        if display_name is not None:
            payload["display_name"] = display_name
        return self._request("POST", "/learners", json=payload)

    def list_learners(self) -> list[dict[str, Any]]:
        return self._request("GET", "/learners")

    def get_learner_profile(self, learner_id: str) -> dict[str, Any]:
        return self._request("GET", f"/learners/{learner_id}")

    def attach_session_to_learner(self, session_id: str, learner_id: str) -> dict[str, Any]:
        return self._request("POST", f"/sessions/{session_id}/attach-learner", json={"learner_id": learner_id})

    def rebuild_learner(self, learner_id: str) -> dict[str, Any]:
        return self._request("POST", f"/learners/{learner_id}/rebuild")

    def get_learner_timeline(self, learner_id: str) -> dict[str, Any]:
        return self._request("GET", f"/learners/{learner_id}/timeline")

    def get_learner_recommendations(self, learner_id: str) -> list[dict[str, Any]]:
        return self._request("GET", f"/learners/{learner_id}/recommendations")

    def get_learning_plan(self, learner_id: str, horizon: int | None = None) -> dict[str, Any]:
        params: dict[str, Any] = {}
        if horizon is not None:
            params["horizon"] = horizon
        return self._request("GET", f"/learners/{learner_id}/learning-plan", params=params or None)

    def get_learner_report(self, learner_id: str) -> dict[str, Any]:
        return self._request("GET", f"/learners/{learner_id}/report")

    def list_modes(self) -> list[dict[str, Any]]:
        return self._request("GET", "/modes")

    def get_mode(self, mode_id: str) -> dict[str, Any]:
        return self._request("GET", f"/modes/{mode_id}")

    def list_presets(self) -> list[dict[str, Any]]:
        return self._request("GET", "/presets")

    def get_preset(self, preset_id: str) -> dict[str, Any]:
        return self._request("GET", f"/presets/{preset_id}")

    def list_assessment_templates(self) -> list[dict[str, Any]]:
        return self._request("GET", "/assessment-templates")

    def get_assessment_template(self, template_id: str) -> dict[str, Any]:
        return self._request("GET", f"/assessment-templates/{template_id}")

    def get_learner_drills(self, learner_id: str) -> list[dict[str, Any]]:
        return self._request("GET", f"/learners/{learner_id}/drills")

    def get_session_mode_status(self, session_id: str) -> dict[str, Any]:
        return self._request("GET", f"/sessions/{session_id}/mode-status")

    def get_session_mode_report(self, session_id: str) -> dict[str, Any]:
        return self._request("GET", f"/sessions/{session_id}/mode-report")

    def list_roster_templates(self) -> list[dict[str, Any]]:
        return self._request("GET", "/roster-templates")

    def get_roster_template(self, roster_template_id: str) -> dict[str, Any]:
        return self._request("GET", f"/roster-templates/{roster_template_id}")

    def get_session_roster(self, session_id: str) -> dict[str, Any]:
        return self._request("GET", f"/sessions/{session_id}/roster")

    def get_session_balance(self, session_id: str) -> dict[str, Any]:
        return self._request("GET", f"/sessions/{session_id}/balance")

    def get_session_group_report(self, session_id: str) -> dict[str, Any]:
        return self._request("GET", f"/sessions/{session_id}/group-report")

    def create_reviewer(self, reviewer_id: str, display_name: str, role_title: str | None = None) -> dict[str, Any]:
        return self._request(
            "POST",
            "/reviewers",
            json={"reviewer_id": reviewer_id, "display_name": display_name, "role_title": role_title},
        )

    def list_reviewers(self) -> list[dict[str, Any]]:
        return self._request("GET", "/reviewers")

    def create_review_pack(self, session_id: str) -> dict[str, Any]:
        return self._request("POST", f"/sessions/{session_id}/review-pack")

    def list_review_packs(self, session_id: str | None = None) -> list[dict[str, Any]]:
        params = {"session_id": session_id} if session_id else None
        return self._request("GET", "/review-packs", params=params)

    def get_review_pack(self, review_pack_id: str) -> dict[str, Any]:
        return self._request("GET", f"/review-packs/{review_pack_id}")

    def submit_review(
        self,
        review_pack_id: str,
        *,
        reviewer_id: str,
        rubric_scores: list[dict[str, Any]] | None = None,
        annotations: list[dict[str, Any]] | None = None,
        override_decisions: list[dict[str, Any]] | None = None,
        overall_judgment: str | None = None,
        summary_notes: list[str] | None = None,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "reviewer_id": reviewer_id,
            "rubric_scores": rubric_scores or [],
            "annotations": annotations or [],
            "override_decisions": override_decisions or [],
            "overall_judgment": overall_judgment,
            "summary_notes": summary_notes or [],
            "metadata": {},
        }
        return self._request("POST", f"/review-packs/{review_pack_id}/submit", json=payload)

    def get_session_review_summary(self, session_id: str) -> dict[str, Any]:
        return self._request("GET", f"/sessions/{session_id}/review-summary")

    def get_session_calibration(self, session_id: str) -> dict[str, Any] | None:
        return self._request("GET", f"/sessions/{session_id}/calibration")

    def list_curriculum_packs(self) -> list[dict[str, Any]]:
        return self._request("GET", "/curriculum-packs")

    def get_curriculum_pack(self, pack_id: str) -> dict[str, Any]:
        return self._request("GET", f"/curriculum-packs/{pack_id}")

    def create_assignment(
        self,
        *,
        pack_id: str,
        learner_ids: list[str],
        title: str,
        created_by: str | None = None,
        description: str | None = None,
    ) -> dict[str, Any]:
        return self._request(
            "POST",
            "/assignments",
            json={
                "pack_id": pack_id,
                "learner_ids": learner_ids,
                "created_by": created_by,
                "title": title,
                "description": description,
            },
        )

    def list_assignments(self, learner_id: str | None = None) -> list[dict[str, Any]]:
        params = {"learner_id": learner_id} if learner_id else None
        return self._request("GET", "/assignments", params=params)

    def get_assignment_progress(self, assignment_id: str) -> dict[str, Any]:
        return self._request("GET", f"/assignments/{assignment_id}/progress")

    def launch_assignment_step(
        self,
        assignment_id: str,
        step_id: str,
        *,
        snapshot_id: str,
        provider_name: str = "mock",
        learner_id: str | None = None,
    ) -> dict[str, Any]:
        return self._request(
            "POST",
            f"/assignments/{assignment_id}/steps/{step_id}/launch-session",
            json={
                "snapshot_id": snapshot_id,
                "provider_name": provider_name,
                "learner_id": learner_id,
            },
        )

    def learner_assignments(self, learner_id: str) -> list[dict[str, Any]]:
        return self._request("GET", f"/learners/{learner_id}/assignments")

    def curriculum_pack_from_plan(
        self,
        learner_id: str,
        *,
        horizon: int,
        output_pack_id: str,
        display_name: str | None = None,
    ) -> dict[str, Any]:
        return self._request(
            "POST",
            f"/learners/{learner_id}/curriculum-pack-from-plan",
            json={
                "horizon": horizon,
                "output_pack_id": output_pack_id,
                "display_name": display_name,
            },
        )

    def list_authoring_artifacts(
        self,
        *,
        artifact_type: str | None = None,
        source_type: str | None = None,
    ) -> list[dict[str, Any]]:
        params = {}
        if artifact_type:
            params["artifact_type"] = artifact_type
        if source_type:
            params["source_type"] = source_type
        return self._request("GET", "/authoring/artifacts", params=params or None)

    def create_authoring_draft(
        self,
        *,
        draft_id: str,
        artifact_type: str,
        artifact_id: str | None = None,
        author_id: str | None = None,
        as_derivative: bool = False,
        initial_content: dict[str, Any] | None = None,
        title: str | None = None,
    ) -> dict[str, Any]:
        return self._request(
            "POST",
            "/authoring/drafts",
            json={
                "draft_id": draft_id,
                "artifact_type": artifact_type,
                "artifact_id": artifact_id,
                "author_id": author_id,
                "as_derivative": as_derivative,
                "initial_content": initial_content,
                "title": title,
            },
        )

    def list_authoring_drafts(self) -> list[dict[str, Any]]:
        return self._request("GET", "/authoring/drafts")

    def get_authoring_draft(self, draft_id: str) -> dict[str, Any]:
        return self._request("GET", f"/authoring/drafts/{draft_id}")

    def validate_authoring_draft(self, draft_id: str) -> dict[str, Any]:
        return self._request("POST", f"/authoring/drafts/{draft_id}/validate", json={})

    def preview_authoring_draft(
        self,
        draft_id: str,
        *,
        preview_kind: str = "pack_walkthrough",
        snapshot_id: str | None = None,
        provider_name: str = "mock",
    ) -> dict[str, Any]:
        return self._request(
            "POST",
            f"/authoring/drafts/{draft_id}/preview",
            json={
                "preview_kind": preview_kind,
                "snapshot_id": snapshot_id,
                "provider_name": provider_name,
            },
        )

    def publish_authoring_draft(self, draft_id: str, *, published_version: str) -> dict[str, Any]:
        return self._request(
            "POST",
            f"/authoring/drafts/{draft_id}/publish",
            json={"published_version": published_version},
        )

    def list_authoring_patches(self) -> list[dict[str, Any]]:
        return self._request("GET", "/authoring/patches")

    def generate_authoring_patches(self, *, source_type: str, source_id: str) -> list[dict[str, Any]]:
        return self._request(
            "POST",
            "/authoring/patches/generate",
            json={"source_type": source_type, "source_id": source_id},
        )

    def apply_authoring_patch(self, draft_id: str, patch_id: str) -> dict[str, Any]:
        return self._request("POST", f"/authoring/drafts/{draft_id}/apply-patch/{patch_id}", json={})

    def list_authoring_publications(self, *, artifact_type: str | None = None) -> list[dict[str, Any]]:
        params = {"artifact_type": artifact_type} if artifact_type else None
        return self._request("GET", "/authoring/publications", params=params)


ApiClient = DiscussionApiClient
