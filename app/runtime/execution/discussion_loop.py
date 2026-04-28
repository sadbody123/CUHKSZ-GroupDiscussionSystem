"""Auto-advance discussion with activation strategy support and optional user filler lines."""

from __future__ import annotations

import threading

from app.runtime.enums import RoleType
from app.runtime.execution.turn_executor import TurnExecutor
from app.runtime.schemas.agent import AgentReply
from app.runtime.schemas.session import SessionContext

_cancel_events: dict[str, threading.Event] = {}


def request_auto_run_cancel(session_id: str) -> None:
    evt = _cancel_events.get(session_id)
    if evt is None:
        evt = threading.Event()
        _cancel_events[session_id] = evt
    evt.set()


def auto_run_discussion(
    executor: TurnExecutor,
    *,
    max_steps: int = 4,
    auto_fill_user: bool = True,
) -> tuple[SessionContext, list[AgentReply]]:
    out: list[AgentReply] = []
    session = executor.session
    consecutive = getattr(session, "allow_consecutive_agent_turns", False)
    session_id = session.session_id

    cancel_evt = _cancel_events.get(session_id)
    if cancel_evt is None:
        cancel_evt = threading.Event()
        _cancel_events[session_id] = cancel_evt
    cancel_evt.clear()

    for step in range(max_steps):
        if cancel_evt.is_set():
            break

        last = session.turns[-1].speaker_role if session.turns else None

        nr = executor.sm.peek_next_role(session, last)
        is_user_turn = nr == RoleType.USER.value

        pending = list(session.activation_queue)
        has_pending = bool(pending)

        if is_user_turn and has_pending:
            rep_result = executor.run_next_turn()
            if rep_result[1]:
                out.append(rep_result[1])
            session = rep_result[0]
            if cancel_evt.is_set():
                break
            continue

        if is_user_turn:
            if not auto_fill_user:
                break
            if not has_pending:
                session = executor.submit_user_turn(
                    getattr(session, "auto_fill_user_prompt", "")
                    or "[auto] Continuing the discussion with a brief follow-up."
                )
            if cancel_evt.is_set():
                break

        rep_result = executor.run_next_turn()
        if rep_result[1] is None:
            if not consecutive:
                break
            continue
        out.append(rep_result[1])
        session = rep_result[0]

    _cancel_events.pop(session_id, None)
    return session, out
