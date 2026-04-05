# Known limitations (final)

- **Advisory only**: readiness, stability, RC, handover bundles, and acceptance evidence are **training / engineering support artifacts** for local verification — **not** formal certification, accreditation, or regulatory compliance.
- **Not an official assessment**: speech metrics, learner analytics, review calibration scores, and practice-mode reports use **heuristics, proxies, or simulation** — they must not be presented as official grades or exam results.
- **Snapshots required**: run **`python main.py bootstrap-dev-snapshot`** (or `build-offline` from `README.md`) so `dev_snapshot_v2` exists under the configured snapshot root.
- **Mock-first**: default flows use **mock** LLM/ASR/TTS; cloud keys are optional. **OpenAI-compatible / vendor providers are not guaranteed to match mock behavior** and are **not** covered to the same depth in CI.
- **Scope**: extended surfaces (audio, group sim, authoring, etc.) may be gated by `v1_demo` or marked experimental — see capability matrix and release profiles.

Additional items may be listed under `storage/stability/issues/issues.yaml`.
