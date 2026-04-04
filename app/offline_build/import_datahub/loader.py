"""Load records from JSON or CSV table exports."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


def _flatten_json_records(raw: Any) -> list[dict[str, Any]]:
    if raw is None:
        return []
    if isinstance(raw, list):
        return [x for x in raw if isinstance(x, dict)]
    if isinstance(raw, dict):
        for key in ("records", "data", "rows", "items", "results"):
            if key in raw and isinstance(raw[key], list):
                return [x for x in raw[key] if isinstance(x, dict)]
        return [raw]
    return []


def load_json_file(path: Path) -> list[dict[str, Any]]:
    text = path.read_text(encoding="utf-8")
    raw = json.loads(text)
    return _flatten_json_records(raw)


def load_csv_file(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append({k: (v if v is not None else "") for k, v in row.items()})
    return rows


def load_table_file(path: Path) -> list[dict[str, Any]]:
    """Load all records from a table export file."""
    suf = path.suffix.lower()
    if suf == ".json":
        return load_json_file(path)
    if suf == ".csv":
        return load_csv_file(path)
    return []
