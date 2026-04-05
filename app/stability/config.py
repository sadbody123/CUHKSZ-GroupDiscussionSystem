"""Paths for bundled stability assets."""

from __future__ import annotations

from pathlib import Path


def bundled_scenarios_dir() -> Path:
    return Path(__file__).resolve().parent / "scenarios"


def project_root() -> Path:
    return Path(__file__).resolve().parents[2]
