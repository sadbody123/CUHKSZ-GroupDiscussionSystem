"""Logging trace contextvars."""

from __future__ import annotations

import logging

from app.logging import setup_logging
from app.ops.trace import (
    reset_eval_run_id,
    reset_request_id,
    reset_session_id,
    set_eval_run_id,
    set_request_id,
    set_session_id,
    trace_extra,
)


def test_trace_context_in_logs(capsys) -> None:
    setup_logging()
    log = logging.getLogger("test_trace")
    tok = set_request_id("rid-1")
    try:
        log.info("hello")
        err = capsys.readouterr().err
        assert "rid-1" in err
    finally:
        reset_request_id(tok)


def test_trace_extra_fields() -> None:
    tr = set_request_id("r")
    ts = set_session_id("s")
    te = set_eval_run_id("e")
    try:
        extra = trace_extra()
        assert extra["request_id"] == "r"
        assert extra["session_id"] == "s"
        assert extra["eval_run_id"] == "e"
    finally:
        reset_request_id(tr)
        reset_session_id(ts)
        reset_eval_run_id(te)
