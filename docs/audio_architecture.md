# Audio architecture (phase 9)

The voice MVP sits **above** the existing text runtime: snapshots, `TurnExecutor`, and session file storage are unchanged. New code lives under `app/audio/` and is consumed through `AudioService` (`app/application/audio_service.py`).

## Layers

1. **Providers** (`app/audio/providers/`): `BaseASRProvider` / `BaseTTSProvider` with `mock_asr`, `mock_tts` as defaults; optional OpenAI-compatible implementations when keys and dependencies exist.
2. **Pipelines** (`app/audio/pipeline/`): thin wrappers for `transcribe` / `synthesize`, plus `AudioStore` for filesystem assets under `AUDIO_STORAGE_DIR` (default `storage/audio/`).
3. **Application**: `AudioService` orchestrates save → ASR/TTS → metadata; `DiscussionService` / `FeedbackService` optionally call TTS after agent or coach text.
4. **API** (`app/api/routers/audio.py`): multipart upload, TTS for a turn, list assets, download by `asset_id`.
5. **UI**: Streamlit uses `DiscussionApiClient` only; no direct filesystem access to audio paths.

## Session integration

`TranscriptTurn` adds `input_mode`, `audio_asset_id`, `transcript_source`, `tts_asset_id`. `SessionContext` adds `audio_enabled`, provider hints, and `audio_asset_ids`. Older JSON sessions load with defaults (`text`-only turns).

## Artifacts

Audio manifests are JSON files under `<AUDIO_STORAGE_DIR>/_manifests/`. The artifact registry (`artifact_kind=audio_asset`) scans these for ops visibility.
