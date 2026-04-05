"""Lexical searcher."""

from __future__ import annotations

from pathlib import Path

from app.indexing.lexical.builder import write_lexical_index
from app.indexing.lexical.searcher import LexicalSearcher


def test_lexical_search_orders(tmp_path: Path) -> None:
    docs = [
        {"item_id": "a", "text": "banana fruit", "title": "t1", "tags": ["food"]},
        {"item_id": "b", "text": "car engine", "title": "t2", "tags": []},
    ]
    p = tmp_path / "lex.json"
    write_lexical_index(p, docs)
    s = LexicalSearcher(p)
    hits = s.search("banana", top_k=2, query_tags=["food"])
    assert hits[0][0] == "a"
