# Practice modes and presets

The `app/modes` package defines **practice modes**, **scenario presets**, **drill specs**, and **assessment templates** as YAML assets loaded through `ModeRegistry` (`app/modes/loaders/yaml_loader.py`).

- **Practice mode** (`PracticeMode`): high-level training intent (e.g. `free_practice`, `micro_drill`, `assessment_simulation`).
- **Preset** (`ScenarioPreset`): bundles a mode with starter prompts, constraint overrides, and optional runtime profile hints.
- **Application**: `ModeService` (`app/application/mode_service.py`) exposes catalog APIs used by CLI, FastAPI, and Streamlit.

Modes are optional: if YAML is missing, the loader degrades gracefully and defaults (see `app/modes/constants.py` and settings) apply.
