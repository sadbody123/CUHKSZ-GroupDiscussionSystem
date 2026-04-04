# Pedagogy knowledge base (offline)

## Purpose

`pedagogy_kb` holds structured teaching artifacts: discussion rules, grading rubrics, language banks, and coaching tips. It is **not** sourced from Datahub; it is maintained as curated JSONL under a pedagogy directory.

## Input layout

Place JSONL files in a directory (e.g. `app/knowledge/pedagogy/raw/` or test fixtures). Recognized filenames:

| File | Default `item_type` |
|------|---------------------|
| `rules.jsonl` | `rule` |
| `rubric.jsonl` | `rubric` |
| `language_bank.jsonl` | `language_bank` |
| `coaching_tips.jsonl` | `coaching_tip` |

Each non-empty line is one JSON object. Missing files are ignored.

## `PedagogyItem` schema

See `app/schemas/pedagogy.py`. Minimum viable row:

- `item_id` (or `id` / `uuid`)
- `content` (non-empty string)

Optional: `item_type` (overrides file default), `category`, `subcategory`, `language`, `source_ref`, `tags`, `metadata`.

## Snapshot output

`pedagogy_items.jsonl` — one `PedagogyItem` per line.

Build statistics appear in `build_report.json` (`pedagogy_files_read`, `pedagogy_lines_read`, `pedagogy_items_out`) and `manifest.json` (`pedagogy_item_count`).
