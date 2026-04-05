"""Load demo scenario YAML."""

from __future__ import annotations

from pathlib import Path

import yaml

from app.release.config import bundled_scenarios_dir
from app.release.schemas.scenario import DemoScenario


def load_demo_scenario(scenario_id: str) -> DemoScenario:
    from app.ops.settings import get_ops_settings

    s = get_ops_settings()
    dirs: list[Path] = []
    sd = getattr(s, "demo_scenario_dir", None)
    if sd:
        dirs.append(Path(sd).resolve())
    dirs.append(bundled_scenarios_dir())
    name = f"{scenario_id}.yaml"
    for d in dirs:
        p = d / name
        if p.is_file():
            raw = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
            raw.setdefault("scenario_id", scenario_id)
            return DemoScenario.model_validate(raw)
    raise FileNotFoundError(f"demo scenario not found: {scenario_id}")


def list_scenario_ids() -> list[str]:
    from app.ops.settings import get_ops_settings

    s = get_ops_settings()
    seen: set[str] = set()
    out: list[str] = []
    dirs: list[Path] = [bundled_scenarios_dir()]
    sd = getattr(s, "demo_scenario_dir", None)
    if sd:
        dirs.insert(0, Path(sd).resolve())
    for d in dirs:
        if not d.is_dir():
            continue
        for f in sorted(d.glob("*.yaml")):
            if f.stem not in seen:
                seen.add(f.stem)
                out.append(f.stem)
    return sorted(out)
