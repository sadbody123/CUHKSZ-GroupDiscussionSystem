# Evidence index (offline)

## Purpose

`evidence_chunks.jsonl` (phase 1) stores chunk-level text for reproducible builds. **`evidence_index.jsonl`** adds training-oriented fields while keeping a stable link to `chunk_id` and `doc_id`:

- `stance_hint` — coarse position label
- `credibility_score` — rule-based trust by source table / type
- `quality_score` — blends chunk quality with length / URL / title heuristics
- `citation` — stable string from title, URL, dates, and ids

No embeddings or vector stores are involved.

## Schema

See `app/schemas/evidence_index.py` (`EvidenceIndexItem`).

## Rules (minimal, explainable)

### `stance_hint`

Allowed values: `for`, `against`, `neutral`, `mixed`, `unknown`.

Heuristics combine keyword cues (support/oppose terms in EN/ZH) with table defaults (e.g. community → `neutral` when no cue).

### `credibility_score` (0–1)

Examples:

- `reports` / official-like `source_type` → higher
- Research / encyclopedia / knowledge tables → medium-high
- Community tables → lower

### `quality_score` (0–1)

Starts from any chunk `quality_score` if present, then nudges by text length, presence of URL/title, and number of tags.

### `citation`

Built from document title, URL, `published_at`, `source_type`, `source_table`, `doc_id`, and `chunk_id` (see `evidence_index/citation.py`).

## Snapshot

`evidence_index_count` appears in `manifest.json`; detailed counts in `build_report.json`.
