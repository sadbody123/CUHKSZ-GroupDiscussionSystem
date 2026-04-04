# Feedback signals (rule-based)

## Pipeline

1. `analyze_transcript_turns` → numeric metrics + `detected_signals` dicts.
2. `build_feedback_packet` → `FeedbackPacket` with strengths/risks strings and optional `recommended_pedagogy_item_ids`.

## Implemented signals

| Signal id | Meaning |
|-----------|---------|
| `long_turn_risk` | Any turn word count > 220 |
| `example_language` | Cues like “for example”, “e.g.” |
| `few_examples_risk` | No example cues detected |
| `discussion_language` | Cues like “I agree”, “in response to” |
| `support_teammate_language` | Support / teammate phrases |
| `response_linkage` | “in response to”, “as for your point”, … |
| `low_interaction_risk` | User turns < `max(1, total_turns // 4)` |

## Future coach LLM

`FeedbackPacket.metrics` and `detected_signals` are stable JSON-friendly inputs; `recommended_pedagogy_item_ids` points at `PedagogyItem.item_id` values for curated follow-up reading.
