"""SHA-256 helpers for snapshot bundles."""

from __future__ import annotations

import hashlib
from pathlib import Path


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            chunk = f.read(65536)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def parse_checksums(content: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for line in content.splitlines():
        line = line.strip()
        if not line:
            continue
        parts = line.split(None, 1)
        if len(parts) != 2:
            continue
        digest, rel = parts[0], parts[1].strip().lstrip("*")
        out[rel.replace("\\", "/")] = digest
    return out
