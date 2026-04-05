# E2E scenario matrix

Bundled YAML specs live in `app/stability/scenarios/`. Each spec maps to existing **release demo** flows or small **service-level** flows (group/audio) that reuse `SessionService`, `DiscussionService`, `GroupService`, etc.

| scenario_id | Typical mapping |
|-------------|-----------------|
| text_core_cli / text_core_api | `text_core_demo` via release runner |
| learner_assignment_flow, curriculum_delivery_flow | `learner_assignment_demo` |
| review_calibration_flow | `review_calibration_demo` |
| group_mode_flow | Roster apply + turns when `group_simulation` enabled |
| audio_optional_flow | Mock audio path or skip when gated |
| full_rc_flow | Readiness + `text_core_demo` |

List via CLI: `python main.py list-e2e-scenarios`.
