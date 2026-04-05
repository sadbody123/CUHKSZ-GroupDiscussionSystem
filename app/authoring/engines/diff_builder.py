"""Deterministic structured diff (dict/list)."""

from __future__ import annotations

from typing import Any


def build_diff(base: Any, draft: Any, path: str = "") -> list[dict[str, Any]]:
    """Return list of change dicts with keys: path, kind, old, new."""
    changes: list[dict[str, Any]] = []
    if type(base) != type(draft) and base is not None and draft is not None:
        changes.append({"path": path or ".", "kind": "replace", "old": base, "new": draft})
        return changes
    if isinstance(base, dict) and isinstance(draft, dict):
        keys = set(base) | set(draft)
        for k in sorted(keys):
            p = f"{path}.{k}" if path else k
            if k not in base:
                changes.append({"path": p, "kind": "add", "old": None, "new": draft[k]})
            elif k not in draft:
                changes.append({"path": p, "kind": "remove", "old": base[k], "new": None})
            else:
                changes.extend(build_diff(base[k], draft[k], p))
        return changes
    if isinstance(base, list) and isinstance(draft, list):
        n = max(len(base), len(draft))
        for i in range(n):
            p = f"{path}[{i}]"
            if i >= len(base):
                changes.append({"path": p, "kind": "add", "old": None, "new": draft[i]})
            elif i >= len(draft):
                changes.append({"path": p, "kind": "remove", "old": base[i], "new": None})
            else:
                changes.extend(build_diff(base[i], draft[i], p))
        return changes
    if base != draft:
        changes.append({"path": path or ".", "kind": "change", "old": base, "new": draft})
    return changes


def summarize_diff(changes: list[dict[str, Any]], max_items: int = 40) -> list[str]:
    lines: list[str] = []
    for c in changes[:max_items]:
        lines.append(f"{c['kind']}: {c['path']}")
    if len(changes) > max_items:
        lines.append(f"... and {len(changes) - max_items} more changes")
    return lines
