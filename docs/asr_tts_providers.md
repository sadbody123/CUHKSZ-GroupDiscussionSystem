# ASR / TTS providers

## Defaults (CI / offline)

| Name | Class | Notes |
|------|--------|--------|
| `mock_asr` | `MockASRProvider` | Reads `tests/fixtures/audio/manifest.json` by basename, or bundled `app/audio/data/mock_asr_manifest.json`; hash fallback for raw bytes. |
| `mock_tts` | `MockTTSProvider` | Deterministic small WAV via `wave` (stdlib). |

## Optional

| Name | Class | Requirements |
|------|--------|----------------|
| `openai_whisper` | `OpenAIWhisperCompatibleProvider` | `OPENAI_API_KEY`, `OPENAI_TRANSCRIBE_MODEL` (optional) |
| `openai_tts` | `OpenAITTSCompatibleProvider` | `OPENAI_API_KEY`, `OPENAI_TTS_MODEL` (optional) |
| `local_whisper_stub` / `local_tts_stub` | Stubs | Delegate to mocks; placeholders for future local engines. |

Resolution: `app/audio/providers/manager.py` + `UnifiedSettings.default_asr_provider` / `default_tts_provider`.
