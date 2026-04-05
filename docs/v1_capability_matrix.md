# V1 capability matrix (human summary)

The **machine-readable** matrix is produced by:

```bash
python main.py show-capability-matrix --profile-id v1_demo
```

or programmatically via `build_capability_matrix_json()` in `app/release/pipeline/build_capability_matrix.py`.

## Columns

| Field | Meaning |
|--------|---------|
| `capability_id` | Stable id used in profiles and gates |
| `area` | Layer: offline_build, runtime, api, ui, eval, … |
| `stability` | `stable` / `beta` / `experimental` / `deferred` |
| `enabled` | Effective enablement for the selected profile |
| `experimental` | Flagged experimental in the profile |

## Bundled capabilities

See `CAPABILITY_LIST` / `all_capabilities()` in `app/release/engines/capability_registry.py` for the authoritative list and metadata.
