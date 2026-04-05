# Recommendation engine

Recommendations are **rule-based and explainable**: each item includes a human-readable `reason`.

Types:

- **topic** — prefers topic cards whose tags/text align with weak skills and avoids recently practiced topic ids when possible.
- **pedagogy** — selects pedagogy KB items by tag overlap with weak skills (with a safe fallback list).
- **runtime_profile** — concise / strict_coach / balanced heuristics from concision and interaction signals.
- **mode** — text / audio / mixed based on speech-proxy weakness and whether audio history exists.
- **micro_drill** — short practice drills tied to weak skills.

The engine caps output size via `LEARNER_RECOMMENDATION_MAX_ITEMS`.
