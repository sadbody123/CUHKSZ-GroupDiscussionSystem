"""Shared cancel signal for V2 runtime auto-run.

Mirrors V1's `discussion_loop._cancel_events` pattern so that
`POST /sessions/{id}/cancel-auto-run` can interrupt both V1 and V2
auto-runs through a single API endpoint.

Usage:
    from app.agent_runtime_v2.facade.cancel_signal import request_cancel, is_cancel_requested

    # In the API handler:
    request_cancel(session_id)

    # In a graph node (runs on the invoking thread):
    if is_cancel_requested(state.session_id):
        state.stop_reason = "cancelled"
        return ...
"""

from __future__ import annotations

import threading

_cancel_events: dict[str, threading.Event] = {}


def request_cancel(session_id: str) -> None:
    evt = _cancel_events.get(session_id)
    if evt is None:
        evt = threading.Event()
        _cancel_events[session_id] = evt
    evt.set()


def is_cancel_requested(session_id: str) -> bool:
    evt = _cancel_events.get(session_id)
    return evt is not None and evt.is_set()


def clear_cancel(session_id: str) -> None:
    _cancel_events.pop(session_id, None)


def get_cancel_event(session_id: str) -> threading.Event:
    if session_id not in _cancel_events:
        _cancel_events[session_id] = threading.Event()
    return _cancel_events[session_id]