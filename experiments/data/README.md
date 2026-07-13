# Data (placeholder)

This directory is intentionally empty in v0.1. **No datasets exist yet.**

When the pilot corpus is authored, it will contain the hand-written, reviewed
prompts organized as matched A/B/C/D groups (see
[`../../preregistration/experimental-design.md`](../../preregistration/experimental-design.md)).
Each item will carry the metadata validated by `ascr.schema.PromptItem`:
`item_id`, `axis`, `domain`, `task_state_present`, `concept_mention_present`,
`prompt_text`, `matched_group_id`, `expected_strategy_space`, `notes`, and the
optional `qa` and `provenance` blocks.

**Run-ready gate (v0.1.1, 2nd pass).** No activations may be extracted until the
whole stimulus set passes `ascr.schema.check_run_ready(...)`: every matched group
run_ready (complete typed QA, `disposition == pass`, `naturalness_rating >= 4`,
within-group naturalness spread ≤ 1 point), the model revision frozen, the
sample-size floor met, and every externally-sourced item carrying a review-approved
provenance record (`ascr.schema.EXTERNAL_PROVENANCE_FIELDS`). External
answerability/unanswerability labels are never used unreviewed; unknown training-data
overlap is documented as *unknown*, not as contamination-free.

No fabricated data will be committed. Extracted activations and model outputs are
generated only after the model revision hash is frozen.
