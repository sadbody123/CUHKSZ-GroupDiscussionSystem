# Providers: mock vs cloud (expectations)

| Capability | Default in demos / CI | Optional cloud / HTTP |
|------------|------------------------|-------------------------|
| LLM | `mock` — deterministic, offline | `openai_compatible` — needs `OPENAI_API_KEY`, **not** parity-tested with mock |
| ASR | `mock_asr` | Vendor-specific providers — need configuration; **not** default delivery guarantee |
| TTS | `mock_tts` | Cloud TTS — optional; behavior differs from mock |

**CI** exercises **mock** providers only. Treat any cloud path as **best-effort** and validate manually before relying on it in a presentation.
