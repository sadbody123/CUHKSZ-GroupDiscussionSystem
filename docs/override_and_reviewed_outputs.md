# Overrides and reviewed outputs

**OverrideDecision** records must include `reason`, `approved`, and stable `override_id` values. Only **approved** overrides are merged into **reviewed outputs** (new JSON artifacts under `storage/reviews/reviewed_outputs/`).

Original `FeedbackPacket` / `CoachReport` files on disk are **never** mutated by the review layer. Reviewed payloads include `review_id`, `reviewer_id`, `created_at`, and a **proxy note** reminding users that metrics are training aids.
