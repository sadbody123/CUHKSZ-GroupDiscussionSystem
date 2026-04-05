"""Structured logging setup with trace context (contextvars)."""

from __future__ import annotations

import json
import logging
import sys
from typing import Any

from app.ops.trace import trace_extra


class _ContextFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        ex = trace_extra()
        record.request_id = ex.get("request_id") or "-"
        record.session_id = ex.get("session_id") or "-"
        record.eval_run_id = ex.get("eval_run_id") or "-"
        record.trace_id = ex.get("trace_id") or "-"
        return True


class _JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "request_id": getattr(record, "request_id", None),
            "session_id": getattr(record, "session_id", None),
            "eval_run_id": getattr(record, "eval_run_id", None),
            "trace_id": getattr(record, "trace_id", None),
        }
        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False)


def configure_logging(*, level: str = "INFO", structured: bool = False) -> None:
    """Configure root logger once; safe to call multiple times (replaces handlers if structured mode changes)."""
    root = logging.getLogger()
    lvl = getattr(logging, level.upper(), logging.INFO)
    root.setLevel(lvl)

    plain_fmt = "%(asctime)s %(levelname)s %(name)s [rid=%(request_id)s sid=%(session_id)s] %(message)s"
    if structured:
        fmt: logging.Formatter = _JsonFormatter()
    else:
        fmt = logging.Formatter(plain_fmt, datefmt="%Y-%m-%dT%H:%M:%S")

    h = logging.StreamHandler(sys.stderr)
    h.setLevel(lvl)
    h.setFormatter(fmt)
    h.addFilter(_ContextFilter())

    root.handlers.clear()
    root.addHandler(h)
