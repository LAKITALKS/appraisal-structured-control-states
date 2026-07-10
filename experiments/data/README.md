# Data (placeholder)

This directory is intentionally empty in v0.1. **No datasets exist yet.**

When the pilot corpus is authored, it will contain the hand-written, reviewed
prompts organized as matched A/B/C/D groups (see
[`../../preregistration/experimental-design.md`](../../preregistration/experimental-design.md)).
Each item will carry the metadata validated by `ascr.schema.PromptItem`:
`item_id`, `axis`, `domain`, `task_state_present`, `concept_mention_present`,
`prompt_text`, `matched_group_id`, `expected_strategy_space`, and `notes`.

No fabricated data will be committed. Extracted activations and model outputs are
generated only after the model revision hash is frozen.
