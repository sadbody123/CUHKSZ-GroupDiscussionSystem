"""CI and deployment asset presence."""

from __future__ import annotations

from pathlib import Path

import yaml

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def test_github_workflow_exists() -> None:
    p = PROJECT_ROOT / ".github" / "workflows" / "ci.yml"
    assert p.is_file()
    data = yaml.safe_load(p.read_text(encoding="utf-8"))
    assert "jobs" in data


def test_docker_files_exist() -> None:
    assert (PROJECT_ROOT / "docker" / "Dockerfile.api").is_file()
    assert (PROJECT_ROOT / "docker" / "Dockerfile.ui").is_file()
    assert (PROJECT_ROOT / "docker" / "docker-compose.yml").is_file()


def test_makefile_optional() -> None:
    m = PROJECT_ROOT / "Makefile"
    if m.is_file():
        txt = m.read_text(encoding="utf-8")
        assert "pytest" in txt or "test" in txt.lower()
