"""Structured JSONL event logger for runtime V2."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class RuntimeEventLogger:
    def __init__(self, event_file: Path) -> None:
        self._event_file = event_file
        self._event_file.parent.mkdir(parents=True, exist_ok=True)

    def log(
        self,
        *,
        run_id: str,
        session_id: str,
        backend: str,
        node_name: str,
        next_actor: str | None,
        stop_reason: str | None,
        success: bool,
        error_summary: str | None = None,
        trace_id: str | None = None,
        checkpoint_id: str | None = None,
        quality_decision: str | None = None,
        interrupt_reason: str | None = None,
        repair_count: int | None = None,
        quality_flags: list[str] | None = None,
        review_id: str | None = None,
        policy_id: str | None = None,
    ) -> dict:
        evt = {
            "timestamp": _utc_now_iso(),
            "run_id": run_id,
            "session_id": session_id,
            "backend": backend,
            "node_name": node_name,
            "next_actor": next_actor,
            "stop_reason": stop_reason,
            "success": success,
            "error_summary": error_summary,
            "trace_id": trace_id,
            "checkpoint_id": checkpoint_id,
            "quality_decision": quality_decision,
            "interrupt_reason": interrupt_reason,
            "repair_count": repair_count,
            "quality_flags": list(quality_flags or []),
            "review_id": review_id,
            "policy_id": policy_id,
        }
        with self._event_file.open("a", encoding="utf-8") as f:
            f.write(json.dumps(evt, ensure_ascii=False) + "\n")
        return evt
