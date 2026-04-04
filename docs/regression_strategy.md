# Regression strategy (phase 6)

## Baselines

- **Smoke suite** (`tests/fixtures/evals/suites/smoke_suite.yaml`) — quick CI-style checks across retrieval, analyzer, state machine, agent (mock), and e2e.
- **Profile comparison** — `compare-profiles` runs the same suite per profile and writes a merged `report.json` / `.md` / `.csv` under the output directory.

## Mock stability

Mock LLM outputs include deterministic `[MOCK::<role>::<hash>]` prefixes; assertions target stable substrings, not full hashes.

## When to extend cases

Add a row to the appropriate `cases/*.yaml`, reference it from a suite, and keep `expected` aligned with rule-based behavior (not model drift).
