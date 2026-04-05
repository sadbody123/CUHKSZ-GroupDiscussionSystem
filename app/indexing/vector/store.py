"""NPY + meta persistence."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np


def save_vector_store(npy_path: Path, meta_path: Path, matrix: np.ndarray, item_ids: list[str]) -> None:
    npy_path.parent.mkdir(parents=True, exist_ok=True)
    np.save(npy_path, matrix.astype(np.float32))
    meta = {"item_ids": item_ids, "dimension": int(matrix.shape[1]) if matrix.size else 0, "count": int(matrix.shape[0])}
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def load_vector_store(npy_path: Path, meta_path: Path) -> tuple[np.ndarray, dict[str, Any]]:
    mat = np.load(npy_path)
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    return mat, meta
