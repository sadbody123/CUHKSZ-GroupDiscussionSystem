# Architecture

## Upstream vs downstream

**CUHKSZ-Datahub** (upstream) owns public data acquisition, parsing, SQLite storage, table-level CSV/JSON export, logging, and compliance. It is treated as an **external dependency**: this project does **not** import upstream ORM, migrations, or internal Python packages.

**CUHKSZ-GroupDiscussionSystem** (this repo) only reads **exported files** (one file per table). It maps rows to a **downstream internal schema** (`NormalizedDocument`, `EvidenceChunk`, etc.) and produces **offline snapshots** suitable for reproducible builds and tests.

## Offline build vs runtime

| Area | Responsibility |
|------|----------------|
| `app/offline_build/` | Import → normalize → dedupe → classify → chunk → write snapshot |
| `app/offline_build/pedagogy/` | Load curated pedagogy JSONL (rules, rubrics, language bank, coaching tips) |
| `app/offline_build/topic_cards/` | Load manual YAML/JSON topic cards + optional bootstrap from evidence tags |
| `app/offline_build/evidence_index/` | Enrich chunks into `EvidenceIndexItem` (stance, scores, citations) |
| `app/runtime/` | Snapshot loader, repositories, rule retrieval / role router, orchestrator, transcript analyzers, optional **LLM abstraction** (mock by default), prompt rendering, agents, file-backed sessions, discussion CLI |
| `app/application/` | Service layer: snapshot/topic/session/discussion/feedback orchestration for API/UI |
| `app/api/` | FastAPI REST API (phase 5) |
| `app/ui/` | Streamlit Web MVP (phase 5) |
| `app/runtime/profiles/` + profile loader | YAML runtime profiles merged with `default` (phase 6) |
| `app/evals/` | Eval suites, runners, reporters, replay (phase 6) |

**Phase 1** delivers core Datahub → snapshot. **Phase 2** adds three offline “warehouses” (pedagogy KB, topic card store, evidence index) when `--pedagogy-dir` and/or `--topic-card-dir` are provided. **Phase 3** adds read-only runtime consumption and planning/analyzer CLI. **Phase 4** adds CLI text practice with **mock or optional OpenAI-compatible** generation, session JSON under `storage/sessions/`, and coach feedback reports. **Phase 5** adds **FastAPI** and **Streamlit** on top of the same runtime and file sessions — still **no** database, login, or vector DB. **Phase 6** adds **runtime profiles** and a file-driven **evaluation / regression / replay** toolkit (CLI-first), without a hosted experiment platform.

## Why offline-first

Snapshots are deterministic, diffable, and easy to validate in CI. They provide a stable contract for future runtime components (retrieval, facilitation, multi-role practice) without coupling this stage to LLM or vector infrastructure.
