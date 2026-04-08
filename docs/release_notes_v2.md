# Release Notes - V2 Delivery Freeze

## Summary

This freeze finalizes a dual-runtime repository with:

- V1 default runtime path (stable baseline)
- V2 graph-native runtime path (LangGraph-backed, opt-in)
- Review workflow and manual override path
- Discussion + Runtime Review frontend consoles
- Transcript and runtime timeline APIs
- OpenAPI-based frontend contract generation
- Playwright mock and real-backend E2E modes

## Key Upgrades vs Earlier Baseline

- Runtime V2 with checkpoint/event/review workflow integrated into app/API.
- Frontend operator surface for sessions and runtime review actions.
- Session detail upgraded with full transcript and timeline panels.
- Contract hardening with generated OpenAPI types and adapter layer.
- CI/testing split into baseline and full-v2-fullstack matrix.

## What Is Not Included In This Release

- LLM-assisted verifier as default quality gate.
- Multi-instance strong-consistency review queue storage.
- Full graph visualization UI.
- Full production platform hardening (auth/multi-tenant/ops SLA).

## Verification Baseline

See:

- `docs/test_matrix.md`
- `docs/final_handover_runbook.md`
- `docs/frontend_codegen_and_e2e.md`

for exact command-level verification paths.
