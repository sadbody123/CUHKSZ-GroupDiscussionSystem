"""Eval paths and defaults."""

from __future__ import annotations

from pathlib import Path


def project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def resolve_path(p: str | Path) -> Path:
    path = Path(p)
    return path if path.is_absolute() else project_root() / path


def cases_search_roots() -> list[Path]:
    return [project_root() / "tests" / "fixtures" / "evals" / "cases"]
