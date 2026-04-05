# Curriculum pack specification

A **CurriculumPack** groups ordered **steps** (`CurriculumPackStep`) with optional links to topics, modes, drills, assessments, rosters, and reviewed-artifact **references** (no overwrites of source artifacts).

Builtin packs ship as YAML in `app/curriculum/packs/`. Custom packs are saved as JSON under `storage/curriculum_packs/custom/`.

Step `success_criteria` values drive deterministic **training completion** checks (e.g. `transcript`, `coach_report`, `mode_report`) — not formal grading.
