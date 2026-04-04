# CUHKSZ-GroupDiscussionSystem

Downstream system for **CUHKSZ-Datahub** table exports. This repository consumes JSON/CSV files exported per upstream table, normalizes them into a unified schema, and builds **offline knowledge snapshots** for future group-discussion / practice runtimes.

## Current scope

### Phase 1 (Datahub → snapshot)

- Import exported table files from a directory
- Adapter-based mapping to `NormalizedDocument`
- Text cleaning, light classification, exact dedupe, character-based chunking
- Write snapshot artifacts under `app/knowledge/snapshots/<snapshot_id>/`

### Phase 2 (three offline warehouses)

When `--pedagogy-dir` and/or `--topic-card-dir` is provided, the build also emits:

- `pedagogy_items.jsonl` — curated rules, rubrics, language bank, coaching tips
- `topic_cards.jsonl` — manual YAML/JSON cards merged with tag-frequency bootstrap
- `evidence_index.jsonl` — enriched evidence rows (stance hint, credibility/quality scores, citations)

### Phase 3 (runtime — consume snapshot, no LLM)

- `app/runtime/` loads snapshots read-only, exposes repositories, rule-based retrieval / `RoleRouter`, session state machine, transcript analyzers, and prompt **placeholders**.
- CLI (requires a phase-2 snapshot such as `dev_snapshot_v2`): `list-topics`, `show-topic`, `retrieve-context`, `plan-turn`, `analyze-transcript`.

### Phase 4 (CLI text practice MVP + LLM abstraction)

- **`app/runtime/llm/`** — provider interface, **mock** (default, offline) and optional **OpenAI-compatible** HTTP provider.
- **`app/runtime/render/`**, **`app/runtime/agents/`**, **`app/runtime/execution/`** — render prompts, run multi-role agents, discussion loop, feedback generation.
- **File sessions** under `storage/sessions/` — `create-session`, `session-status`, `submit-user-turn`, `run-next-turn`, `auto-run-discussion`, `generate-feedback`, `export-session`.

**Still not included:** hosted multi-tenant auth, vector DB with embeddings, speech, or live crawling. Real LLM calls are **optional** (env + provider); mock runs without API keys.

See [CLI discussion MVP](docs/cli_discussion_mvp.md) and [LLM integration](docs/llm_integration.md).

### Phase 5 (FastAPI + Streamlit MVP)

- **`app/application/`** — service layer wrapping runtime (snapshots, topics, sessions, discussion, feedback).
- **`app/api/`** — FastAPI app with REST endpoints; same services as CLI.
- **`app/ui/`** — Streamlit single-page UI calling the API via **`httpx`**.
- Commands: `python main.py run-api`, `python main.py run-ui`.

See [Application service layer](docs/application_service_layer.md), [API MVP](docs/api_mvp.md), [Streamlit UI](docs/streamlit_ui_mvp.md), and [Local runbook](docs/local_runbook.md).

## Requirements

- Python 3.11+

## Install

```bash
cd CUHKSZ-GroupDiscussionSystem
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev]"
```

Copy `.env.example` to `.env` if you want to override defaults (optional).

## Build an offline snapshot (phase 1 only)

```bash
python main.py build-offline --input-dir tests/fixtures/datahub_exports --snapshot-id dev_snapshot
```

Outputs (`schema_version` `1.0`):

- `manifest.json`, `build_report.json`
- `normalized_docs.jsonl`, `evidence_chunks.jsonl`, `source_catalog.jsonl`

## Build with pedagogy + topic cards (phase 2)

```bash
python main.py build-offline ^
  --input-dir tests/fixtures/datahub_exports ^
  --pedagogy-dir tests/fixtures/pedagogy ^
  --topic-card-dir tests/fixtures/topic_cards ^
  --snapshot-id dev_snapshot_v2
```

Equivalent (requires at least one of `--pedagogy-dir` / `--topic-card-dir`):

```bash
python main.py build-knowledge --input-dir tests/fixtures/datahub_exports --pedagogy-dir tests/fixtures/pedagogy --topic-card-dir tests/fixtures/topic_cards --snapshot-id dev_snapshot_v2
```

Phase 2 adds `pedagogy_items.jsonl`, `topic_cards.jsonl`, `evidence_index.jsonl` and sets `schema_version` to `1.1`.

Optional: set `SNAPSHOT_ROOT` to redirect output root (see `.env.example`).

## Validate a snapshot

```bash
python main.py validate-snapshot --snapshot-dir app/knowledge/snapshots/dev_snapshot
```

For `1.1` snapshots, validation also requires the three phase-2 JSONL files.

## Runtime CLI (phase 3)

After building `dev_snapshot_v2` (see above):

```bash
python main.py list-topics --snapshot-dir app/knowledge/snapshots/dev_snapshot_v2
python main.py show-topic --snapshot-dir app/knowledge/snapshots/dev_snapshot_v2 --topic-id tc-campus-ai
python main.py retrieve-context --snapshot-dir app/knowledge/snapshots/dev_snapshot_v2 --topic-id tc-campus-ai --role ally --phase discussion --top-k 5
python main.py plan-turn --snapshot-dir app/knowledge/snapshots/dev_snapshot_v2 --topic-id tc-campus-ai --phase discussion --last-role user --transcript-file tests/fixtures/runtime/sample_transcript.json
python main.py analyze-transcript --snapshot-dir app/knowledge/snapshots/dev_snapshot_v2 --topic-id tc-campus-ai --transcript-file tests/fixtures/runtime/sample_transcript.json
```

## Discussion CLI (phase 4)

Uses the same snapshot; sessions are stored under `storage/sessions/` (override with `--storage-root`). Use **`--provider mock`** for offline runs.

```bash
python main.py create-session --snapshot-dir app/knowledge/snapshots/dev_snapshot_v2 --topic-id tc-campus-ai --user-stance for --provider mock
python main.py session-status --session-id <session_id>
python main.py submit-user-turn --session-id <session_id> --text "Your line of argument."
python main.py run-next-turn --session-id <session_id>
python main.py auto-run-discussion --session-id <session_id> --max-steps 4
python main.py generate-feedback --session-id <session_id>
python main.py export-session --session-id <session_id> --output-file tmp/session_export.json
```

Details: [docs/cli_discussion_mvp.md](docs/cli_discussion_mvp.md).

## Tests

```bash
pytest -q
```

## Documentation

- [Architecture](docs/architecture.md)
- [Data contract & field assumptions](docs/data_contract.md)
- [Build pipeline](docs/build_pipeline.md)
- [Pedagogy KB](docs/pedagogy_kb.md)
- [Topic cards](docs/topic_cards.md)
- [Evidence index](docs/evidence_index.md)
- [Runtime architecture](docs/runtime_architecture.md)
- [Retrieval / role router](docs/retrieval_router.md)
- [Session state machine](docs/session_state_machine.md)
- [Feedback signals](docs/feedback_signals.md)
- [LLM integration (phase 4)](docs/llm_integration.md)
- [Prompt rendering (phase 4)](docs/prompt_rendering.md)
- [CLI discussion MVP (phase 4)](docs/cli_discussion_mvp.md)
- [Coach report (phase 4)](docs/coach_report.md)
- [Application service layer (phase 5)](docs/application_service_layer.md)
- [API MVP (phase 5)](docs/api_mvp.md)
- [Streamlit UI MVP (phase 5)](docs/streamlit_ui_mvp.md)
- [Local runbook (phase 5)](docs/local_runbook.md)
