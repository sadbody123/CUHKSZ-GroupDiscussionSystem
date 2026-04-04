# Topic cards (offline)

## Purpose

Topic cards describe practice prompts: stances, bullet points, pitfalls, and links back to evidence. They support **manual authoring** plus a **minimal rule-based bootstrap** from frequent evidence tags.

## `TopicCard` schema

Defined in `app/schemas/topic_card.py`. Key fields include `topic_id`, `topic`, optional stances, `core_points_for` / `core_points_against`, `example_hints`, `related_doc_ids`, `related_chunk_ids`, and `tags`.

Legacy `title` is accepted; if `topic` is empty it is filled from `title`.

## Manual input

Directory of `*.yaml`, `*.yml`, or `*.json` files. Supported shapes:

- A list of card objects
- `{ "topics": [ ... ] }` or `{ "cards": [ ... ] }`
- A single object

Each card needs at least `topic_id` and `topic` (or `title`).

## Bootstrap rules

When the knowledge layer is enabled:

1. Count `topic_tags` across `evidence_chunks`
2. For top tags **not** already covered by a manual card’s `topic` / `tags`, emit `TopicCard` rows with `topic_id` like `bootstrap:<tag>`
3. Fill `related_doc_ids`, `related_chunk_ids`, and short `example_hints` from chunk text

`core_points_for` / `against`, `pitfalls`, and `common_questions` may remain empty in bootstrap rows.

## Snapshot output

`topic_cards.jsonl` — merged manual + bootstrap cards (manual wins on `topic_id` collision).

Counts: `topic_cards_manual`, `topic_cards_bootstrapped`, `topic_cards_out` in `build_report.json`; `topic_card_count` in `manifest.json`.
