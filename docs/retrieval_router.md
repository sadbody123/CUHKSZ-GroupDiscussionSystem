# Retrieval and role router

## Principles

- **Rule-based only**: keyword overlap, scores on `evidence_index`, `item_type` / tags for pedagogy.
- **No embeddings** and no vector store.

## `RoleRouter.build_context_packet`

For each `role` + `topic_id` + `session_phase`:

| Role | Pedagogy emphasis | Evidence emphasis |
|------|--------------------|-------------------|
| `moderator` | `rule`, `language_bank` | light / optional |
| `coach` | `rubric`, `coaching_tip` | few rows, topic-tagged if possible |
| `ally` | `language_bank` | topic tags, `stance_hint=for` preferred |
| `opponent` | `language_bank` | topic tags, `stance_hint=against` preferred |
| `user` | minimal | summary-oriented metadata |

Ranking uses `retrieval/ranker.py` (topic match, credibility, quality, keyword hits, coarse `source_type` weight).

## Prompt template ids

`prompt_loader.prompt_template_id_for_role` maps to files in `app/runtime/prompts/` (e.g. `moderator.md`).
