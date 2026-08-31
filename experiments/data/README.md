# Data (placeholder)

This directory is intentionally empty in v0.1.2. **No datasets exist yet.**

When the pilot corpus is authored, it will contain the hand-written, reviewed
prompts organized as matched A/B/C/D groups (see
[`../../preregistration/experimental-design.md`](../../preregistration/experimental-design.md)).
Each item will carry the metadata validated by `ascr.schema.PromptItem`:
`item_id`, `axis`, `domain`, `task_state_present`, `concept_mention_present`,
`prompt_text`, `matched_group_id`, `expected_strategy_space`, `notes`, and the
optional `qa` and `provenance` blocks.

**Run-ready gate (v0.1.2).** No activations may be extracted until the
whole stimulus set passes `ascr.schema.check_run_ready(...)`: every matched group
run_ready (complete typed QA, `disposition == pass`, `naturalness_rating >= 4`,
within-group naturalness spread ≤ 1 point, observed factor values matching the
item, and explicit non-target-axis absence), model/tokenizer and prompt-embedding
revisions frozen, the sample-size floor met, and every external item carrying a review-approved
provenance record (`ascr.schema.EXTERNAL_PROVENANCE_FIELDS`). External
answerability/unanswerability labels are never used unreviewed; unknown training-data
overlap is documented as *unknown*, not as contamination-free.

No fabricated data will be committed. The current draft config and unfrozen
Mini-0 template block scientific generation. Technical smoke prompts and logs are
kept outside this scientific data path and are never eligible for analysis.
