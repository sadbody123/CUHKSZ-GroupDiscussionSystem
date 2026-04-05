"""Load small JSON manifests for snapshots and bundles."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def snapshot_manifest(snapshot_dir: Path) -> dict[str, Any] | None:
    p = snapshot_dir / "manifest.json"
    if not p.is_file():
        return None
    try:
        return read_json(p)
    except (OSError, json.JSONDecodeError):
        return None
