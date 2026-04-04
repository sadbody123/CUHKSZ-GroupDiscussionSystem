"""Eval case / suite loaders."""

from __future__ import annotations

from app.evals.loaders.dataset_loader import load_case, reload_cases
from app.evals.loaders.suite_loader import load_suite
from tests.conftest import PROJECT_ROOT


def test_load_smoke_case():
    reload_cases()
    c = load_case("smoke_retrieval")
    assert c.case_type == "retrieval_case"


def test_load_smoke_suite():
    p = PROJECT_ROOT / "tests" / "fixtures" / "evals" / "suites" / "smoke_suite.yaml"
    s = load_suite(p)
    assert s.suite_id == "smoke"
    assert "smoke_e2e" in s.case_refs
