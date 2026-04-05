# Learner plan → curriculum bridge

When `ENABLE_PLAN_TO_PACK_BRIDGE` is on, `CurriculumService.create_curriculum_pack_from_learning_plan` builds a **draft pack** from a generated `LearningPlan` (weak skills, recommendations). Steps are explainable and tagged with `reason: from_learning_plan`.

Use `POST /learners/{learner_id}/curriculum-pack-from-plan` or CLI `create-pack-from-learning-plan`. The draft can be edited (export JSON, adjust, save as custom pack) before creating assignments.
