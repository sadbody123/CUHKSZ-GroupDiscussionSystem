"""Optional upstream export manifest (simplified)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def read_optional_manifest(export_dir: Path) -> dict[str, Any] | None:
    """
    If `export_dir/manifest.json` exists, parse and return it.
    Otherwise None. Does not validate upstream schema.
    """
    p = export_dir / "manifest.json"
    if not p.is_file():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
