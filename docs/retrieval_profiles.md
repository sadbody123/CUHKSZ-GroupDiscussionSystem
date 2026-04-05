# Retrieval profiles

Runtime profiles merge over `default.yaml`. New retrieval keys include:

- `mode`: `rule` | `lexical` | `vector` | `hybrid`
- `use_indexes_if_available`: bool
- `lexical_top_k`, `vector_top_k`, `final_top_k`
- `lexical_weight`, `vector_weight`
- `title_boost`, `topic_tag_boost`, `quality_boost`, `credibility_boost`

Example: `app/runtime/profiles/hybrid_default.yaml` sets `mode: hybrid` with balanced weights.
