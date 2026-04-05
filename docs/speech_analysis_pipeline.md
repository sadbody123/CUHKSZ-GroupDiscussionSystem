# Speech analysis pipeline

1. **Resolve config** — `resolve_speech_config()` merges `UnifiedSettings`, runtime profile `speech_analysis`, and defaults.
2. **Load audio** — bytes from `AudioStore` by `audio_asset_id` on user turns.
3. **Analyze** — `LocalWaveAnalyzer` (default) runs extractors → `DeliveryMetrics` → rule-based `DeliverySignal`s → `SpeechAnalysisPacket`.
4. **Session** — aggregate packets → `SessionSpeechReport`, saved under `SPEECH_REPORT_DIR`.
5. **Feedback** — optional merge into `FeedbackPacket` / `CoachReport` when `with_speech_analysis` is set.
