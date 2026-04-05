# Learner analytics limitations

- **No accounts or authentication** — `learner_id` is a local label only.
- **No database** — JSON files; no concurrency guarantees beyond atomic writes.
- **Heuristic skills** — transcript rules + optional speech aggregates; not psychometrically validated.
- **Speech** — delivery/fluency numbers are **proxy** indicators for practice feedback, not pronunciation certification.
- **Recommendations / plans** — transparent rules, not ML ranking; quality is “good enough to train,” not optimal scheduling.
