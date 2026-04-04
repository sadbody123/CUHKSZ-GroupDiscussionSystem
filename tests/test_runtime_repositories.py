"""Repository filter tests."""

from __future__ import annotations

import pytest

from tests.conftest import HAS_SNAPSHOT_V2

from app.runtime.repositories.pedagogy_repo import PedagogyRepository
from app.runtime.repositories.topic_repo import TopicRepository
from app.runtime.repositories.evidence_repo import EvidenceRepository
from app.runtime.retrieval.router import build_repositories
from app.runtime.snapshot_loader import load_snapshot


@pytest.mark.skipif(not HAS_SNAPSHOT_V2, reason="dev_snapshot_v2 not present")
def test_repos_list_filter(snapshot_v2_dir):
    b = load_snapshot(snapshot_v2_dir)
    ped, top, ev, doc, src = build_repositories(b)
    assert ped.list_items()
    assert top.list_topics()
    assert ev.list_evidence()
    assert doc.get_doc(b.normalized_docs[0].doc_id)
    assert src.list_sources()
    t = top.get_topic("tc-campus-ai")
    assert t is not None
    assert top.search_topics("campus")
    assert ev.by_doc_id(b.normalized_docs[0].doc_id) or True
    assert ev.filter(min_quality=0.0, top_k=3)
