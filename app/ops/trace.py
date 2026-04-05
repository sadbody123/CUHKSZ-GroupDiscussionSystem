"""Request / session / eval trace context (contextvars)."""

from __future__ import annotations

import contextvars
import uuid
from typing import Any

request_id_var: contextvars.ContextVar[str | None] = contextvars.ContextVar("request_id", default=None)
session_id_var: contextvars.ContextVar[str | None] = contextvars.ContextVar("session_id", default=None)
eval_run_id_var: contextvars.ContextVar[str | None] = contextvars.ContextVar("eval_run_id", default=None)
trace_id_var: contextvars.ContextVar[str | None] = contextvars.ContextVar("trace_id", default=None)


def new_trace_id() -> str:
    return str(uuid.uuid4())


def set_request_id(rid: str | None) -> contextvars.Token[str | None]:
    return request_id_var.set(rid)


def reset_request_id(token: contextvars.Token[str | None]) -> None:
    request_id_var.reset(token)


def get_request_id() -> str | None:
    return request_id_var.get()


def set_session_id(sid: str | None) -> contextvars.Token[str | None]:
    return session_id_var.set(sid)


def reset_session_id(token: contextvars.Token[str | None]) -> None:
    session_id_var.reset(token)


def get_session_id() -> str | None:
    return session_id_var.get()


def set_eval_run_id(rid: str | None) -> contextvars.Token[str | None]:
    return eval_run_id_var.set(rid)


def reset_eval_run_id(token: contextvars.Token[str | None]) -> None:
    eval_run_id_var.reset(token)


def get_eval_run_id() -> str | None:
    return eval_run_id_var.get()


def set_trace_id(tid: str | None) -> contextvars.Token[str | None]:
    return trace_id_var.set(tid)


def get_trace_id() -> str | None:
    return trace_id_var.get()


def trace_extra() -> dict[str, Any]:
    return {
        "request_id": get_request_id(),
        "session_id": get_session_id(),
        "eval_run_id": get_eval_run_id(),
        "trace_id": trace_id_var.get(),
    }
