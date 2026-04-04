# Data contract

## Supported export tables (phase 1)

Files are discovered by **filename stem** matching a supported table name, with extension `.json` or `.csv`:

| Priority | Table | Adapter module |
|----------|-------|----------------|
| High | `reports` | `adapters/reports.py` |
| High | `research_outputs` | `adapters/research_outputs.py` |
| High | `knowledge_entities` | `adapters/knowledge_entities.py` |
| High | `research_projects` | `adapters/research_projects.py` |
| High | `encyclopedia_entries` | `adapters/encyclopedia_entries.py` |
| Medium | `community_articles` | `adapters/community_articles.py` |
| Medium | `community_pages` | `adapters/community_pages.py` |
| Medium | `community_events` | `adapters/community_events.py` |

`posts` and `comments` are **not** registered in this phase.

## Field assumptions (best-effort)

Adapters use tolerant lookups. **Strong dependency:** at least one of the following must yield usable text after stripping, or the row is skipped:

- Common content keys: `content`, `body`, `text`, `description`, `summary`, `abstract`, `markdown`, `html`, …
- Or a usable `title` / `name` / `headword` string long enough to pass the minimum length filter (default 20 characters after cleaning).

**Optional** (filled when present):

- Identifiers: `id`, `_id`, `uuid`, table-specific ids (`slug`, `doi`, …)
- URLs: `url`, `link`, `permalink`, …
- Dates: `published_at`, `created_at`, `updated_at`, `start_time`, …
- Language: `language`, `lang`, `locale` — if missing, a coarse hint may be inferred from character classes.

Unknown columns are preserved in `NormalizedDocument.metadata` where JSON-serializable.

## JSON shapes

- Preferred: a **JSON array** of row objects.
- Also accepted: an object with a list under `records`, `data`, `rows`, `items`, or `results`.

## CSV

UTF-8 with optional BOM; first row is headers. Values map to the same logical field names as JSON.

## When upstream changes

- Prefer **adding** new optional keys in exports; adapters already pass unknown fields to `metadata`.
- If a column is renamed, extend the adapter’s `first_str` / `first_text` key lists (small, localized change).
- Avoid breaking removal of primary text fields without providing an alternative long-text column.

## Fixtures

`tests/fixtures/datahub_exports/*.json` illustrate minimal plausible rows for local runs and CI.

## Phase 2 inputs (non-Datahub)

| Source | Format | Notes |
|--------|--------|--------|
| Pedagogy | JSONL files in a directory | See `docs/pedagogy_kb.md` |
| Topic cards | YAML / JSON in a directory | See `docs/topic_cards.md` |
| Evidence index | Derived | No separate user upload; see `docs/evidence_index.md` |

These inputs are optional; missing files are skipped without failing the build when the knowledge layer is enabled.
