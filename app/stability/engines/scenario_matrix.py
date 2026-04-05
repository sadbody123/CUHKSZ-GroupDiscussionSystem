"""Discover and load E2E scenario YAML specs."""

from __future__ import annotations

from pathlib import Path

import yaml

from app.stability.config import bundled_scenarios_dir
from app.stability.schemas.scenario import E2EScenarioSpec


def list_scenario_paths(extra_dir: Path | None = None) -> list[Path]:
    roots = [bundled_scenarios_dir()]
    if extra_dir and extra_dir.is_dir():
        roots.append(extra_dir)
    out: list[Path] = []
    for root in roots:
        if not root.is_dir():
            continue
        out.extend(sorted(root.glob("*.yaml")))
    return out


def load_spec(path: Path) -> E2EScenarioSpec:
    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return E2EScenarioSpec.model_validate(raw)


def list_e2e_scenarios(extra_dir: Path | None = None) -> list[E2EScenarioSpec]:
    return [load_spec(p) for p in list_scenario_paths(extra_dir)]


def get_e2e_scenario(scenario_id: str, extra_dir: Path | None = None) -> E2EScenarioSpec | None:
    for p in list_scenario_paths(extra_dir):
        spec = load_spec(p)
        if spec.scenario_id == scenario_id:
            return spec
    return None
