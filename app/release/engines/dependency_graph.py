"""Capability dependency expansion."""

from __future__ import annotations

from app.release.engines.capability_registry import get_capability


def expand_required(capability_ids: set[str]) -> set[str]:
    """Include transitive requires."""
    out = set(capability_ids)
    changed = True
    while changed:
        changed = False
        for cid in list(out):
            c = get_capability(cid)
            if not c:
                continue
            for r in c.requires:
                if r not in out:
                    out.add(r)
                    changed = True
    return out


def dependency_summary() -> dict[str, list[str]]:
    from app.release.engines.capability_registry import all_capabilities

    return {c.capability_id: list(c.requires) for c in all_capabilities()}
