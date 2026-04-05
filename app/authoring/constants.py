"""Authoring / curation / publication constants."""

# Draft status
DS_DRAFT = "draft"
DS_VALIDATED = "validated"
DS_PREVIEWED = "previewed"
DS_PUBLISHED = "published"
DS_ARCHIVED = "archived"

# Patch status
PS_PROPOSED = "proposed"
PS_APPLIED = "applied"
PS_REJECTED = "rejected"
PS_ARCHIVED = "archived"

# Source types
SRC_BUILTIN = "builtin"
SRC_CUSTOM_PUBLISHED = "custom_published"
SRC_DERIVED = "derived"
SRC_REVIEW_GENERATED = "review_generated"
SRC_LEARNER_GENERATED = "learner_generated"

# Patch source types (generator)
PATCH_SRC_REVIEW = "review"
PATCH_SRC_LEARNER = "learner"
PATCH_SRC_EVAL = "eval"
PATCH_SRC_MANUAL = "manual"
PATCH_SRC_CURRICULUM = "curriculum"

# Artifact kinds (authorable)
AT_TOPIC_CARD = "topic_card"
AT_PEDAGOGY_ITEM = "pedagogy_item"
AT_DRILL_SPEC = "drill_spec"
AT_CURRICULUM_PACK = "curriculum_pack"
AT_SCENARIO_PRESET = "scenario_preset"
AT_ASSESSMENT_TEMPLATE = "assessment_template"
AT_ROSTER_TEMPLATE = "roster_template"
AT_RUNTIME_PROFILE = "runtime_profile"

AUTHORABLE_TYPES: tuple[str, ...] = (
    AT_TOPIC_CARD,
    AT_PEDAGOGY_ITEM,
    AT_DRILL_SPEC,
    AT_CURRICULUM_PACK,
    AT_SCENARIO_PRESET,
    AT_ASSESSMENT_TEMPLATE,
    AT_ROSTER_TEMPLATE,
    AT_RUNTIME_PROFILE,
)

PROXY_NOTE = (
    "Authoring inputs from review outputs, learner analytics, or evals are training/curation aids only; "
    "they are not official standards."
)
