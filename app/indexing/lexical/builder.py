"""Build lexical JSON index from normalized docs list."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def write_lexical_index(path: Path, docs: list[dict[str, Any]]) -> None:
    payload = {"schema_version": "1.0", "docs": docs}
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
