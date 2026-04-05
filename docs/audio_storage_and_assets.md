# Audio storage and assets

## Layout

Default root: `storage/audio/` (`AUDIO_STORAGE_DIR`).

```
<audio root>/
  _manifests/
    <asset_id>.json      # AudioAssetRecord JSON
  <session_id>/
    uploads/               # user_upload
    synthesized/           # agent_tts, coach_tts
```

## Record schema

See `app/audio/schemas/audio.py` — `AudioAssetRecord` includes `asset_id`, `session_id`, `turn_id`, `asset_kind`, paths, MIME, optional `transcript_text`, and `metadata`.

## Limits

- `MAX_AUDIO_UPLOAD_MB` (default 25) enforced in `AudioService` and API routes.

## Export

- CLI: `export-audio-asset --asset-id ... --output-file ...`
- API: `GET /audio/{asset_id}`
