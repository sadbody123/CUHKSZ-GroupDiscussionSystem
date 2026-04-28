# CUHKSZ Group Discussion System

## AI-Powered Structured Group Discussion Training

[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18-61DAFB.svg)](https://react.dev/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-pytest%20%2B%20vitest%20%2B%20playwright-8A2BE2.svg)](#testing)

---

## What is This?

CUHKSZ Group Discussion System is an **offline-first, multi-agent group discussion training platform**. It simulates structured academic group discussions with multiple AI agents (Moderator, Ally, Opponent, Coach), providing learners with an immersive practice environment backed by domain-specific knowledge retrieval.

Unlike free-form chat bots, this system enforces **structured discussion phases** (Prepare → Intro → Discussion → Summary → Feedback), supports **evidence-based argument retrieval**, and provides **quality-gated runtime execution** with human-in-the-loop review.

## Core Design Principles

1. **Structured over free-form** — Explicit phase progression with role-bound turn-taking, not unbounded chat.
2. **Role-native context assembly** — Each agent retrieves purpose-built evidence (pro/con for Ally/Opponent, rules for Moderator, rubrics for Coach).
3. **Quality-auditable runtime** — V2 runtime provides heuristic quality gates, repair loops, and interrupt-for-review workflows.
4. **Offline-first** — Pure local operation with JSON file persistence. Zero cloud dependencies for knowledge data.

## Features at a Glance

| Feature | Description |
|---|---|
| Multi-Agent Discussion | Moderator, Ally, Opponent, Coach — four role types with role-directed evidence retrieval |
| Dual Runtime Engine | V1 imperative (default) + V2 LangGraph with quality gating |
| Activation Strategies | Natural (mentions + talkativeness), List (ordered), Pooled (round-robin), Manual (user-designated) — adapted from SillyTavern's group-chats |
| Context Injection Modes | SWAP (current speaker only) / APPEND (all agents visible) for inter-agent awareness |
| Quality Review | V2: pass / repair / interrupt-for-review with human approve/reject/resume/edit-draft |
| Session Management | Create, resume, transcript API, runtime timeline API |
| Practice Modes | Presets, drills, assessments, curriculum packs — full training lifecycle |
| Audio Support | ASR speech-to-text + TTS text-to-speech |
| Full-Stack Testing | Pytest + Vitest + Playwright E2E (mock + real backend) |

## Quick Start

### Minimal (V1, no LangGraph)

```bash
pip install -e ".[dev]"
python main.py bootstrap-dev-snapshot
python -m pytest -m "not v2_graph" -q
python main.py run-api --host 127.0.0.1 --port 8000
```

### Full (V1 + V2 + Frontend)

```bash
pip install -e ".[dev,graph]"
python main.py bootstrap-dev-snapshot

# Terminal 1 — Backend
python main.py run-api --host 127.0.0.1 --port 8000

# Terminal 2 — Frontend
cd frontend
npm install
npm run codegen:openapi
npm run dev
```

Open `http://localhost:5173` and:
1. Create a session (pick a snapshot + topic)
2. Submit a user turn
3. Run next turn
4. Try different activation strategies
5. Open Runtime Reviews if a quality interrupt occurs

## Architecture

```
┌──────────────────┐     ┌───────────────────┐     ┌───────────────────┐
│  React Frontend   │────▶│  FastAPI Backend   │────▶│  Runtime Engine    │
│  Vite + TypeScript │     │  17 Router Modules │     │                    │
└──────────────────┘     └───────────────────┘     ├───────────────────┤
                                                    │  V1: TurnExecutor  │
                                                    │  · State Machine   │
                                                    │  · RoleRouter      │
                                                    │  · LLM Providers   │
                                                    ├───────────────────┤
                                                    │  V2: LangGraph     │
                                                    │  · StateGraph      │
                                                    │  · Quality Gating  │
                                                    │  · Review Queue    │
                                                    │  · Checkpoints     │
                                                    └───────────────────┘
```

### V1 vs V2 Runtime

| | V1 (Default) | V2 (Opt-in) |
|---|---|---|
| **Paradigm** | Imperative state machine | LangGraph StateGraph |
| **Quality Control** | Post-hoc feedback only | pass / repair / interrupt gates |
| **Human Review** | Not supported | Approve / Reject / Resume / Edit Draft |
| **Checkpointing** | FileSessionStore (JSON) | FileCheckpointStore + Event Logger |
| **Resume** | Not supported | Full checkpoint-based resume |
| **Dependency** | None | `langgraph` (pip install -e ".[graph]") |
| **Selection** | `agent_runtime_backend=v1` | `agent_runtime_backend=v2` |

## Documentation

| Document | Content |
|---|---|
| [docs/local_runbook.md](docs/local_runbook.md) | Local install / run / test instructions |
| [docs/agent_runtime_v2.md](docs/agent_runtime_v2.md) | V2 runtime architecture and boundaries |
| [docs/review_workflow_v2.md](docs/review_workflow_v2.md) | Review workflow details |
| [docs/runtime_timeline_v2.md](docs/runtime_timeline_v2.md) | Transcript / timeline API contract |
| [docs/frontend_discussion_console.md](docs/frontend_discussion_console.md) | Discussion console notes |
| [docs/frontend_runtime_review_console.md](docs/frontend_runtime_review_console.md) | Review console notes |
| [docs/frontend_codegen_and_e2e.md](docs/frontend_codegen_and_e2e.md) | OpenAPI codegen + Playwright usage |
| [docs/test_matrix.md](docs/test_matrix.md) | Official minimal / full test matrix |
| [docs/release_scope_and_freeze.md](docs/release_scope_and_freeze.md) | Scope freeze and backlog boundary |
| [KNOWN_LIMITATIONS_FINAL.md](KNOWN_LIMITATIONS_FINAL.md) | Known limits and non-goals |

## Testing

| Layer | Command | Coverage |
|---|---|---|
| Python baseline | `pytest -m "not v2_graph" -q` | V1 + service layer |
| Python full | `pytest -q` | V1 + V2 + LangGraph |
| Frontend unit | `cd frontend && npm run test` | Vitest + React Testing Library |
| E2E Mock | `cd frontend && npm run e2e:mock` | Playwright with mocked backend |
| E2E Real | `cd frontend && npm run e2e:real` | Playwright against real backend |
| Quality Gate | `cd frontend && npm run quality:guard` | codegen → test → build |

## Tech Stack

| Layer | Technology |
|---|---|
| Backend Framework | Python 3.11+ / FastAPI / Pydantic v2 |
| V1 Runtime | Imperative state machine + RoleRouter + LLM provider abstraction |
| V2 Runtime | LangGraph StateGraph + QualityPolicy + ReviewQueueStore |
| CLI | Typer |
| Frontend | React 18 / TypeScript 5.6 / Vite 5.4 |
| State Management | TanStack React Query v5 |
| Routing | React Router DOM v6 |
| API Contract | openapi-typescript codegen |
| E2E Tests | Playwright 1.54 |
| Persistence | JSON files (FileSessionStore, FileCheckpointStore) |

## Known Limitations

- Review queue is file-backed and single-node oriented (not distributed-consensus storage)
- Verifier remains heuristic-first by default
- Timeline UI is list-oriented (not a DAG visual graph)
- Persistence is JSON file-based, no database backend
- Not positioned as multi-tenant production SaaS

See [KNOWN_LIMITATIONS_FINAL.md](KNOWN_LIMITATIONS_FINAL.md) for full details.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) (if available) — pull requests, feature suggestions, and issue reports are welcome.

## License

MIT — see [LICENSE](LICENSE)
