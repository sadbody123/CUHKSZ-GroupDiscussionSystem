"""Eval CLI registration."""

from __future__ import annotations

from pathlib import Path

from app.evals.cli.commands import register_eval_cli


def test_register_eval_cli_is_callable():
    assert callable(register_eval_cli)


def test_eval_cli_module_lists_commands():
    from app.evals.cli import commands as m

    src = Path(m.__file__).read_text(encoding="utf-8")
    assert "list-profiles" in src and "run-evals" in src
