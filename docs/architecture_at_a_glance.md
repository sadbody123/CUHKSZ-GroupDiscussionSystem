# Architecture at a glance

```
CUHKSZ-Datahub (upstream export)
        │
        ▼
offline_build → snapshot (pedagogy / topic cards / evidence)
        │
        ▼
runtime (sessions, retrieval, agents) ← application ← API / UI
        │
        ├── release (profiles, readiness, demo scenarios)
        ├── stability (E2E matrix, RC gate)
        └── handover (manifest, BOM, kits, acceptance)
```
