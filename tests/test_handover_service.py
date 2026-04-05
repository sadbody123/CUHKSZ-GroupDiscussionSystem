"""HandoverService smoke."""

from __future__ import annotations

from pathlib import Path

import pytest

from app.application.handover_service import HandoverService


def test_build_release_manifest(api_test_config) -> None:
    svc = HandoverService(api_test_config)
    out = svc.build_release_manifest("v1_demo")
    m = out.get("manifest") or {}
    assert m.get("profile_id") == "v1_demo"
    assert m.get("included_artifact_refs")


def test_verify_delivery_runs(api_test_config) -> None:
    svc = HandoverService(api_test_config)
    rep = svc.verify_delivery("v1_demo")
    assert rep.get("overall_status") in ("ok", "warning", "blocked")


@pytest.mark.parametrize("name", ["README.md", "QUICKSTART.md", "KNOWN_LIMITATIONS_FINAL.md"])
def test_handover_docs_exist(name: str) -> None:
    root = Path(__file__).resolve().parents[1]
    assert (root / name).is_file()
