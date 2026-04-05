# Learning plan generation

Plans contain **3–5 steps** (horizon from `DEFAULT_LEARNING_PLAN_HORIZON` or API query). Each step includes objective, suggested `topic_id`, `runtime_profile_id`, `mode`, `focus_skills`, and linked pedagogy ids when available.

Generation consumes the same recommendation snapshot as the learner’s last associated session (`snapshot_dir` on the session file). If no session has been attached yet, plan/report endpoints may return an error asking to attach a session first.

Plans are persisted under `storage/learners/<id>/plans/` when generated via CLI or when `persist=True` in the service (API `learning-plan` uses persistence).
