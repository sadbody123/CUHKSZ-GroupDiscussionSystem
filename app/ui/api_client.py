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

    def get_health(self) -> dict[str, Any]:
        return self._request("GET", "/health")

    def list_snapshots(self) -> list[dict[str, Any]]:
        return self._request("GET", "/snapshots")

    def get_snapshot(self, snapshot_id: str) -> dict[str, Any]:
        return self._request("GET", f"/snapshots/{snapshot_id}")

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
        return self._request("POST", "/sessions", json=payload)

    def list_sessions(self) -> list[dict[str, Any]]:
        return self._request("GET", "/sessions")

    def get_session(self, session_id: str) -> dict[str, Any]:
        return self._request("GET", f"/sessions/{session_id}")

    def submit_user_turn(self, session_id: str, text: str) -> dict[str, Any]:
        return self._request("POST", f"/sessions/{session_id}/turns/user", json={"text": text})

    def run_next_turn(self, session_id: str) -> dict[str, Any]:
        return self._request("POST", f"/sessions/{session_id}/run-next")

    def auto_run(self, session_id: str, max_steps: int) -> dict[str, Any]:
        return self._request("POST", f"/sessions/{session_id}/auto-run", json={"max_steps": max_steps})

    def generate_feedback(self, session_id: str) -> dict[str, Any]:
        return self._request("POST", f"/sessions/{session_id}/feedback")

    def export_session(self, session_id: str) -> dict[str, Any]:
        return self._request("GET", f"/sessions/{session_id}/export")
