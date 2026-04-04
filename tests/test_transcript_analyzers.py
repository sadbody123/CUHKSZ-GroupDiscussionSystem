"""Transcript rule analyzers."""

from __future__ import annotations

import json
from pathlib import Path

from app.runtime.evaluation.analyzers import analyze_transcript_turns
from app.runtime.schemas.transcript import TranscriptTurn

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "runtime"


def test_example_and_discussion_signals():
    raw = json.loads((FIXTURE / "sample_transcript.json").read_text(encoding="utf-8"))
    turns = [TranscriptTurn.model_validate(t) for t in raw["turns"]]
    metrics, sigs = analyze_transcript_turns(turns)
    ids = {s["id"] for s in sigs}
    assert metrics["total_turns"] == 2
    assert "example_language" in ids or "discussion_language" in ids


def test_long_turn_risk():
    long_text = " ".join([f"w{i}" for i in range(230)])
    turns = [TranscriptTurn(turn_id="t1", speaker_role="user", text=long_text, created_at="")]
    metrics, sigs = analyze_transcript_turns(turns)
    assert metrics["max_turn_words"] > 220
    assert any(s.get("id") == "long_turn_risk" for s in sigs)


def test_low_interaction_risk():
    raw = json.loads((FIXTURE / "sample_transcript_low_interaction.json").read_text(encoding="utf-8"))
    turns = [TranscriptTurn.model_validate(t) for t in raw["turns"]]
    _m, sigs = analyze_transcript_turns(turns)
    assert any(s.get("id") == "low_interaction_risk" for s in sigs)
