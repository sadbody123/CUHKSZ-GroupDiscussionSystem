# Embedding providers

| name | class | Notes |
|------|-------|--------|
| `hash` | `HashEmbedder` | Default for CI/tests; deterministic; no network. |
| `sentence_transformers` | `SentenceTransformersEmbedder` | Optional; requires `sentence-transformers` and model files. |
| `openai` | `OpenAIEmbeddingProvider` | Optional; needs `OPENAI_API_KEY` and HTTP access. |

Use `get_embedder(name, dimension=128)` from `app.indexing.embedders`.
