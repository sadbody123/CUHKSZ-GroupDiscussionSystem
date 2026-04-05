# Speech workflow MVP

## User audio → turn

1. Upload bytes (CLI, API multipart, or UI).
2. `AudioService.submit_user_audio_turn`: validate size → save `user_upload` asset → `MockASRProvider` (or configured ASR) → append user `TranscriptTurn` with `input_mode=audio`, `transcript_source=asr`.
3. Session saved via existing `FileSessionStore`.

## AI text → speech

1. Caller chooses when to synthesize (CLI `--with-tts`, API query params, UI checkboxes).
2. `AudioService.synthesize_turn_audio` loads turn text, calls TTS, saves `agent_tts` or `coach_tts`, sets `turn.tts_asset_id` or `coach_report["tts_asset_id"]`.

## Playback

- **API**: `GET /audio/{asset_id}` returns bytes with `Content-Type` from the asset record.
- **UI**: client calls the same route and passes bytes to `st.audio`.

No streaming, WebRTC, or ffmpeg in this phase.
