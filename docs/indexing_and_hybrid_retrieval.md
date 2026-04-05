# Indexing and hybrid retrieval (phase 8)

## Overview

- **Offline**: `build_snapshot_indexes()` writes `indexes/` under a snapshot (lexical JSON + optional `vector_embeddings.npy`).
- **Runtime**: `RoleRouter` loads indexes via `try_load_indexes(snapshot_dir)` when `retrieval.mode` is `lexical`, `vector`, or `hybrid` and `use_indexes_if_available` is true.
- **Fallback**: If indexes are missing or a mode cannot run (e.g. vector files absent), the router falls back to the existing **rule** ranker.

## Modes

| mode | Behavior |
|------|----------|
| `rule` | Legacy `ranker` only (default). |
| `lexical` | Lexical scoring over indexed docs. |
| `vector` | Cosine similarity using stored embeddings + query embedding. |
| `hybrid` | Normalized lexical + vector scores (`hybrid/merger.py`) plus quality/credibility boosts for evidence. |

## CLI

- `python main.py build-index --snapshot-id ...`
- `python main.py inspect-index --snapshot-id ...`
- `python main.py search-evidence ...` / `search-pedagogy ...`
- `python main.py benchmark-retrieval --suite-file tests/fixtures/evals/suites/retrieval_benchmark.yaml ...`

See also [index_artifacts.md](index_artifacts.md) and [retrieval_profiles.md](retrieval_profiles.md).
