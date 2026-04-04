"""Load pedagogy JSONL files from a directory."""

from __future__ import annotations

import json
from pathlib import Path

from app.offline_build.pedagogy.validators import row_to_pedagogy_item
from app.schemas.pedagogy import PedagogyItem

_EXPECTED_FILES: dict[str, str] = {
    "rules.jsonl": "rule",
    "rubric.jsonl": "rubric",
    "language_bank.jsonl": "language_bank",
    "coaching_tips.jsonl": "coaching_tip",
}


def _read_jsonl(path: Path, default_item_type: str) -> tuple[list[PedagogyItem], int]:
    items: list[PedagogyItem] = []
    lines = 0
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            lines += 1
            try:
                raw = json.loads(line)
            except json.JSONDecodeError:
                continue
            if not isinstance(raw, dict):
                continue
            pi = row_to_pedagogy_item(raw, default_item_type=default_item_type)
            if pi:
                items.append(pi)
    return items, lines


def load_pedagogy_directory(pedagogy_dir: Path | None) -> tuple[list[PedagogyItem], int, int]:
    """
    Load all expected JSONL files if present.

    Returns (items, files_read, lines_read).
    """
    if pedagogy_dir is None or not pedagogy_dir.is_dir():
        return [], 0, 0
    all_items: list[PedagogyItem] = []
    files_read = 0
    lines_read = 0
    for fname, default_type in _EXPECTED_FILES.items():
        p = pedagogy_dir / fname
        if not p.is_file():
            continue
        files_read += 1
        items, nlines = _read_jsonl(p, default_type)
        lines_read += nlines
        all_items.extend(items)
    return all_items, files_read, lines_read
