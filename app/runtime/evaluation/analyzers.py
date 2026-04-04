"""Rule-based transcript metrics (no LLM)."""

from __future__ import annotations

from app.runtime.enums import RoleType
from app.runtime.evaluation import signals
from app.runtime.schemas.transcript import TranscriptTurn


def analyze_transcript_turns(
    turns: list[TranscriptTurn],
    analyzer_config: dict | None = None,
) -> tuple[dict, list[dict]]:
    """Return (metrics, detected_signals)."""
    cfg = analyzer_config or {}
    long_w = int(cfg.get("long_turn_word_threshold", 220))
    ex_kw = cfg.get("example_keywords")
    disc_kw = cfg.get("discussion_language_keywords")
    sup_kw = cfg.get("support_teammate_keywords")
    link_kw = cfg.get("response_linkage_keywords")
    example_cues = tuple(ex_kw) if ex_kw else signals.EXAMPLE_CUES
    disc_cues = tuple(disc_kw) if disc_kw else signals.DISCUSSION_LANG_CUES
    sup_cues = tuple(sup_kw) if sup_kw else signals.SUPPORT_TEAM_CUES
    link_cues = tuple(link_kw) if link_kw else signals.LINKAGE_CUES

    user_turns = [t for t in turns if t.speaker_role.lower() == RoleType.USER.value]
    lengths = [len(t.text.split()) for t in turns]
    metrics: dict = {
        "total_turns": len(turns),
        "user_turns": len(user_turns),
        "avg_turn_words": round(sum(lengths) / len(lengths), 3) if lengths else 0.0,
        "max_turn_words": max(lengths) if lengths else 0,
    }
    det: list[dict] = []

    if metrics["max_turn_words"] > long_w:
        det.append({"id": "long_turn_risk", "severity": "medium", "detail": "At least one turn is very long."})

    example_hits = sum(1 for t in turns if signals.contains_any(t.text, example_cues))
    if example_hits:
        det.append({"id": "example_language", "severity": "info", "count": example_hits})
    else:
        det.append({"id": "few_examples_risk", "severity": "low", "detail": "Few explicit example cues detected."})

    disc_hits = sum(1 for t in turns if signals.contains_any(t.text, disc_cues))
    if disc_hits:
        det.append({"id": "discussion_language", "severity": "info", "count": disc_hits})

    if any(signals.contains_any(t.text, sup_cues) for t in turns):
        det.append({"id": "support_teammate_language", "severity": "info"})

    if any(signals.contains_any(t.text, link_cues) for t in turns):
        det.append({"id": "response_linkage", "severity": "info"})

    ratio = float(cfg.get("low_interaction_min_ratio", 0.25))
    need = max(1, int(len(turns) * ratio))
    if len(user_turns) < need:
        det.append({"id": "low_interaction_risk", "severity": "high", "detail": "User turns are sparse."})

    return metrics, det
