# Speech feedback integration

- **CLI / API**: `generate-feedback` with `--with-speech-analysis` or `with_speech_analysis=true` runs `SpeechAnalysisService.analyze_session_speech` before coach generation when enabled.
- **Failure isolation**: if speech analysis raises, feedback falls back to text-only coach (exception caught in `FeedbackService`).
- **Artifacts**: turn JSON and `session_report.json` are registered as `speech_analysis_report` for ops scanning.
