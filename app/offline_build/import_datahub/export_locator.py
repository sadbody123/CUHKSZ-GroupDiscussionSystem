"""Discover JSON/CSV exports and derive logical table names from filenames."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from app.offline_build.adapters.registry import SUPPORTED_TABLES


@dataclass(frozen=True)
class ExportFile:
    """A single upstream export file."""

    path: Path
    table_name: str


def _table_from_stem(stem: str) -> str | None:
    s = stem.lower().strip()
    if s in SUPPORTED_TABLES:
        return s
    return None


def locate_exports(input_dir: Path) -> list[ExportFile]:
    """List supported JSON/CSV files under input_dir (non-recursive)."""
    if not input_dir.is_dir():
        return []
    out: list[ExportFile] = []
    for p in sorted(input_dir.iterdir()):
        if not p.is_file():
            continue
        if p.suffix.lower() not in (".json", ".csv"):
            continue
        table = _table_from_stem(p.stem)
        if table:
            out.append(ExportFile(path=p, table_name=table))
    return out
