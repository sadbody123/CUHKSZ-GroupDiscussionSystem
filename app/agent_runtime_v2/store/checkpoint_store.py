"""Minimal file-backed checkpoint store for runtime V2.

This store is intentionally separate from session storage. SessionContext remains
the business source of truth; checkpoints only persist graph control state.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from app.agent_runtime_v2.state.graph_state import DiscussionGraphState


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class FileCheckpointStore:
    def __init__(self, root_dir: Path) -> None:
        self._root = root_dir
        self._root.mkdir(parents=True, exist_ok=True)

    def _run_file(self, run_id: str) -> Path:
        return self._root / f"{run_id}.json"

    def save(self, state: DiscussionGraphState, *, status: str) -> str:
        checkpoint_id = f"ckpt-{uuid4()}"
        payload = {
            "run_id": state.run_id,
            "session_id": state.session_id,
            "status": status,
            "run_status": state.run_status,
            "last_successful_node": state.last_successful_node,
            "emitted_turn_ids": list(state.emitted_turn_ids or []),
            "review_id": state.review_id,
            "policy_id": state.policy_id,
            "updated_at": _utc_now_iso(),
            "checkpoint_id": checkpoint_id,
            "state": state.model_dump(mode="json"),
        }
        self._run_file(state.run_id).write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        return checkpoint_id

    def load(self, run_id: str) -> dict | None:
        p = self._run_file(run_id)
        if not p.is_file():
            return None
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return None

    def load_latest_for_session(self, session_id: str) -> dict | None:
        latest_payload: dict | None = None
        latest_ts = ""
        for f in self._root.glob("*.json"):
            try:
                payload = json.loads(f.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                continue
            if str(payload.get("session_id")) != session_id:
                continue
            ts = str(payload.get("updated_at") or "")
            if ts > latest_ts:
                latest_ts = ts
                latest_payload = payload
        return latest_payload
