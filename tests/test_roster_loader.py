"""Roster template loading."""

from __future__ import annotations

from app.group_sim.loaders.yaml_loader import get_roster_registry


def test_roster_registry_has_4p() -> None:
    reg = get_roster_registry()
    t = reg.get("gd_4p_balanced")
    assert t is not None
    assert t.total_participants == 4
    assert len(t.participants) == 4
