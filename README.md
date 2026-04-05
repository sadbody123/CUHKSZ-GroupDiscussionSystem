# CUHKSZ-GroupDiscussionSystem

Downstream system for **CUHKSZ-Datahub** table exports. This repository consumes JSON/CSV files exported per upstream table, normalizes them into a unified schema, and builds **offline knowledge snapshots** for future group-discussion / practice runtimes.

## Delivery scope (what this repo is meant for)

**Core delivery (best tested, recommended for demo / thesis / handover):**

- Offline **knowledge snapshot** build from table exports (+ optional pedagogy / topic cards).
- **Text group discussion** runtime: sessions, turns, rule + LLM abstraction with **`mock` provider by default** (fully offline).
- **FastAPI** + **Streamlit** MVP wired to the same application services as the CLI.
- Optional **indexing** (lexical / hybrid) with safe fallback to rule retrieval when indexes are absent.

**Explicitly not guaranteed as “production SaaS”:** multi-tenant auth, hosted vector DB at scale, or vendor SLAs. Extended subsystems (audio, learner analytics, group sim, curriculum, authoring, release/stability/handover tooling) are **engineering and research surfaces** — use **advisory / training support** outputs only; see `KNOWN_LIMITATIONS_FINAL.md`.

**Recommended demo path:** `mock` LLM + `mock` ASR/TTS + snapshot `dev_snapshot_v2`. **OpenAI-compatible LLM** and **cloud ASR/TTS** are **optional**, may require API keys, and are **not** asserted to behave like `mock` in CI.

**Version:** `0.1.0` from `pyproject.toml` (exposed via `GET /health` and `app/ops/version.py`).

### Stablest way to run locally

1. `python -m venv .venv` and `pip install -e ".[dev]"` (**required** for API, UI, and pytest).
2. `python main.py bootstrap-dev-snapshot` (or `make bootstrap-dev-snapshot`) — builds `dev_snapshot_v2` from `tests/fixtures` if missing.
3. `python main.py validate-env`
4. `python main.py run-smoke --snapshot-id dev_snapshot_v2 --topic-id tc-campus-ai --provider mock --runtime-profile default`
5. Optional UI: `python main.py run-api` then `python main.py run-ui` — see `docs/DEMO_UI_CHECKLIST.md`.

### Current limitations (short)

- Snapshot **must** exist under the configured snapshot root (`bootstrap-dev-snapshot` or `build-offline` from `README` below).
- Release/stability/handover reports are **local advisory tooling**, not formal certification.
- Speech metrics, learner analytics, and review calibration are **heuristic / proxy** — not official assessment results.

More detail: `KNOWN_LIMITATIONS_FINAL.md`, `QUICKSTART.md`, `DEMO_SCRIPT.md`, `docs/DEMO_UI_CHECKLIST.md`.

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

### Phase 6 (runtime profiles + evaluation / replay)

- **`app/runtime/profiles/*.yaml`** + **`profile_loader` / `profile_resolver`** — merged configuration for retrieval, orchestration, analyzer thresholds, and reply length limits.
- **`SessionContext.runtime_profile_id`** — persisted on sessions; wired through `TurnExecutor`, `run_agent_turn`, and feedback analysis.
- **`app/evals/`** — suite/case schemas, runners, reporters, replay engine, **`run-evals` / `compare-profiles` / `replay-session`** CLI (plus **`list-profiles` / `show-profile`**).
- **API:** `GET /profiles`, `GET /profiles/{id}`; sessions create/status include **`runtime_profile_id`**.
- **Streamlit:** runtime profile dropdown when creating a session.

Docs: [Runtime profiles](docs/runtime_profiles.md), [Evaluation framework](docs/evaluation_framework.md), [Regression strategy](docs/regression_strategy.md), [Session replay](docs/session_replay.md).

### Phase 7 (engineering & delivery)

- **`app/ops/`** — unified `UnifiedSettings` (`.env`), `validate-environment`, artifact registry, snapshot bundle export/import, logging + `contextvars` trace IDs.
- **CLI:** `validate-env`, `list-artifacts`, `inspect-artifact`, `export-snapshot-bundle`, `import-snapshot-bundle`, `run-smoke`.
- **API:** `RequestContextMiddleware` (`X-Request-ID`), extended `GET /health`, `GET /system/info`.
- **Streamlit:** sidebar **System** panel (health + system info) and richer **Debug** fields; graceful handling when the API is down.
- **Docker / Makefile / CI:** `docker/Dockerfile.*`, `docker-compose.yml`, `Makefile`, `.github/workflows/ci.yml` (pytest + validate-env + smoke + minimal evals).

Docs: [Engineering hardening](docs/engineering_hardening.md), [Snapshot bundle spec](docs/snapshot_bundle_spec.md), [Local deployment](docs/local_deployment.md), [Observability & logging](docs/observability_and_logging.md), [CI & release](docs/ci_and_release.md).

### Phase 8 (local lexical / vector / hybrid retrieval)

- **`app/indexing/`** — embedders (`HashEmbedder` default), lexical + vector stores, hybrid merger.
- **`indexes/`** under each snapshot — optional manifest + per-store indexes; **runtime falls back to rule retrieval** if missing.
- **`RoleRouter`** — profile-driven `retrieval.mode`; same `RoleContextPacket` / agents pipeline.
- **CLI**: `build-index`, `inspect-index`, `search-evidence`, `search-pedagogy`, `benchmark-retrieval`.
- **API**: `GET /snapshots/{snapshot_id}/index-status`; session status includes `retrieval_mode` and `has_indexes`.
- **Eval**: `indexed_retrieval_case` + `retrieval_benchmark.yaml` suite.

Docs: [Indexing & hybrid retrieval](docs/indexing_and_hybrid_retrieval.md), [Embedding providers](docs/embedding_providers.md), [Retrieval profiles](docs/retrieval_profiles.md), [Index artifacts](docs/index_artifacts.md).

## Requirements

- Python 3.11+

## Install

**Recommended for developers (API + UI + tests):**

```bash
cd CUHKSZ-GroupDiscussionSystem
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev]"
```

`pip install -e .` installs only the core library (no FastAPI, Streamlit, or pytest). Use that only if you consume the package as a library without running the stack.

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

### One-step demo snapshot (`dev_snapshot_v2`)

If tests or demos expect `dev_snapshot_v2` and it is missing:

```bash
python main.py bootstrap-dev-snapshot
# or: make bootstrap-dev-snapshot
```

This builds from `tests/fixtures` into your configured `SNAPSHOT_ROOT` (default `app/knowledge/snapshots/`). Use `--force` to rebuild.

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

- [Cross-platform notes](docs/cross_platform.md)
- [UI demo checklist](docs/DEMO_UI_CHECKLIST.md)
- [Providers: mock vs optional cloud](docs/providers_truth_table.md)
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
- [Runtime profiles (phase 6)](docs/runtime_profiles.md)
- [Evaluation framework (phase 6)](docs/evaluation_framework.md)
