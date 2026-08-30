# Preregistered Experimental Design

**Status:** v0.1.2 pre-data methodological correction; no data collected. All numbers
below are *planned* pilot parameters, not results.

This document specifies the pilot: the factorial design, the candidate axes and
domains, the model and activation-extraction plan, and the dataset construction
rules. Probing, transfer, intervention, and controls are detailed in
[`analysis-plan.md`](analysis-plan.md) and
[`controls-and-baselines.md`](controls-and-baselines.md). The correction is logged
in [`amendment-v0.1.2.md`](amendment-v0.1.2.md).

---

## 1. Core 2x2 design

For each candidate axis, and holding the broad semantic task fixed, we construct
four conditions:

| Actual task state | Appraisal concept mentioned | Cell | Interpretation |
| --- | --- | --- | --- |
| absent | absent | A | neutral control |
| absent | present | B | concept tracking only |
| present | absent | C | pure task induction |
| present | present | D | combined condition |

The **actual task state** factor manipulates the model's *own* situation (e.g. the
task genuinely lacks the information needed to answer). The **concept mention**
factor manipulates whether appraisal-related vocabulary appears in the prompt
(e.g. the words "uncertain", "conflict", "out of my control"), *without* changing
the underlying task.

Prompts are built in **matched groups**: one base task instantiated across all
four cells so that A/B/C/D differ only along the two intended factors. Each matched
group shares a `matched_group_id`.

The primary H1 analysis uses **double-crossed transfer**: fit task-state decoding on
A/C and evaluate on B/D, then reverse B/D → A/C, always across an outer held-out
domain and whole matched groups. This directly tests whether task-state decoding
survives a change in concept-mention level. The historical v0.1.1 B/C
accuracy-difference statistic is non-identifying and is non-deciding after v0.1.2.

---

## 2. Candidate axes

### Primary pilot axes (definitions sharpened in v0.1.1, 2nd pass)

The three primary axes are defined so their **task-state-present** conditions are
mutually exclusive; controllability is explicitly separated from unanswerability and
from norm tension.

1. **Uncertainty / unanswerability.** Task state present = the information needed to
   answer is **missing**, or the question is **undecidable as posed**. Crucially, the
   model would in principle have a permissible answer/action path **if the missing
   information were supplied**. Concept mention = the prompt uses uncertainty
   vocabulary.
2. **Low controllability / coping capacity.** Task state present = the
   decision-relevant information **is present** and the model **can determine what
   would need to be done**, but **execution is impossible** because a tool, access,
   action channel, or actual means of acting is missing. Missing information must
   **not** be the reason; a norm/policy conflict must **not** be the reason.
   *Example structure:* "Here is the full content and the desired change. Apply the
   change directly in the external system." — the model knows the action but has no
   access. Concept mention = the prompt uses control/coping vocabulary.
3. **Norm tension (rule / instruction conflict).** Task state present = information
   **and** in-principle capability are present, but **two instructions, norms, or
   admissible requirements collide**. Concept mention = the prompt uses
   conflict/tension vocabulary.

### Axis-isolation rule (machine-readable in v0.1.2)

**Primary matched groups may manipulate only one primary axis at a time.** The
item's typed `axis` is its target. Run-ready QA records
`observed_task_state_present` and `observed_concept_mention_present`, which must
exactly equal the registered item values (task state false in A/B and true in C/D;
concept mention false in A/C and true in B/D). The mapping
`non_target_axes_absent_confirmed` must contain exactly the other two primary axes,
each `true`, in addition to `primary_axis_isolated: true`. This is validated by
`ascr.schema`; a free-text note is insufficient. Multi-axis items are admissible
**only** as a separately labelled secondary robustness set and **must not** enter
the primary single-axis analysis. Legacy partial v0.1.1 QA can be read in `draft`
mode but cannot pass v0.1.2 `run_ready`.

### Secondary / exploratory axes

- **Signed relevance** and **goal congruence** are treated as exploratory unless a
  strong, checkable operationalization is provided during dataset construction.
  They are not load-bearing for the primary analysis.

Axes may be correlated; we do not require geometric orthogonality (see
[`analysis-plan.md`](analysis-plan.md)).

---

## 3. Domains

At least four semantically distinct domains, chosen so that no single sensitive
topic dominates the dataset:

1. **Software debugging** (e.g. diagnosing a failing function from a snippet).
2. **Scheduling and planning** (e.g. arranging constrained meetings/resources).
3. **Policy-constrained assistance** (e.g. a helpdesk bound by an explicit policy).
4. **Document editing / creative problem solving** (e.g. revising or completing a
   text under constraints).

The design permits training probes on several domains and evaluating on a
**held-out domain** (leave-one-domain-out), which is the key generalization test.

---

## 4. Item counts (pilot, justified as a pilot)

This is a pilot sized for feasibility on a single open-weight model, **not** a
powered confirmatory study. No formal power analysis is claimed because none has
been performed.

Planned initial counts:

- 3 primary axes x 4 domains x 4 cells (A/B/C/D) = 48 design combinations.
- Target ~24 matched groups per axis (balanced across domains) → ~24 x 4 = 96
  items per axis → ~288 items across the 3 primary axes.
- Plus a neutral/general-task holdout set (~60 items) for competence checks and
  false-positive estimation.

Total initial pilot corpus target: **~350 hand-authored, reviewed prompts.**

### Study stages (clarified in v0.1.1, 2nd pass)

To avoid presenting any count as a powered study, three stages are distinguished:

1. **Feasibility (mini-shards, §9).** ASCR-Mini-0 targets **≥ 40 complete matched
   groups** on the uncertainty axis alone, spread as evenly as feasible across the
   four domains, all A/B/C/D cells per group. This is a **feasibility size**, not a
   power analysis, and yields effect-size/variance estimates.
2. **Pilot.** The ~24 matched-groups-per-axis / ~350-prompt figures above are an
   **early pilot-stage target**, explicitly **not** a powered study.
3. **Confirmatory.** Final sizes are fixed by a documented **power/precision
   analysis** (using feasibility estimates), frozen in a versioned pre-data run plan
   **before** any confirmatory data collection.

### Scaling plan (later, not part of Mini-0)

If the pilot shows a signal that survives the controls, scale to: more matched
groups per axis (target ~200/axis), the two exploratory axes, an additional
held-out domain, and a replication model. A power analysis will be run *before*
the scaled confirmatory study using pilot effect-size estimates.

---

## 5. Model and activation plan

### Primary model

```
Qwen/Qwen2.5-7B-Instruct
```

An open-weight, instruction-tuned model in the ~7B–9B range. **The exact immutable
model revision hash must be recorded in the run config before any data
generation.** The tokenizer revision is frozen separately, and the exact chat
template is recorded. Decoding settings (temperature, top-p, max tokens, seed) are
fixed and recorded per run.

### Replication model (constraint tightened in v0.1.1)

A second open-weight instruction-tuned model of comparable scale may be named for
replication in the scaling phase. **It must not be `Qwen/Qwen2.5-7B-Instruct`
again** (v0.1.1 amendment): replication on the identical model would not test
model-independence. Until a documented, compatibility-checked choice is made (e.g.
a comparable Llama- or Gemma-Instruct model), the config holds the placeholder
`TO_BE_SELECTED_BEFORE_CONFIRMATORY_REPLICATION`. Naming a model here does **not**
imply that replication has been performed; no replication has been run. The config
loader rejects a replication model equal to the primary model once a real model is
set.

### Activation extraction

We record residual-stream activations at:

- the **final prompt-token position** immediately before generation; and
- a small, preregistered set of **early generated-token positions** (e.g. the
  first `k` generated tokens).

Across:

- **all residual-stream layers**, or a preregistered subset if compute-limited.

We keep four notions strictly distinct and label every stored activation with all
four:

- **token position** (index in the sequence),
- **network layer** (residual-stream depth),
- **prompt state** vs
- **generated response state**.

Every stored activation row carries: `item_id`, `axis`, `domain`, `cell` (A/B/C/D),
`task_state_present`, `concept_mention_present`, `matched_group_id`, layer, token
position, and a `prompt_vs_generated` flag.

### Token indexing and Layer 0 (v0.1.2 correction)

The final prompt-token index is the greatest index with `attention_mask == 1`, so
the rule is independent of padding side. A tokenizer-only inspection on disposable
strings at the nonbinding Qwen repository snapshot
`a09a35458c702b33eeacc393d103063234e8bc28` found that the final token produced by
the intended assistant-generation template is newline token ID 198 and that the
last four template tokens were identical across the inspected prompts. This loaded
no model weights and produced no ASCR observation. The binding tokenizer revision
remains an unresolved run blocker.

For hidden transformer layers, the primary readout remains the final non-padding
prompt token. At **Layer 0**, that identical assistant-prefix final-token embedding
is only a sanity check. The informative baseline is the mean-pooled embedding over
the explicitly marked user-visible content span, using
`user_content AND attention_mask AND NOT special_token`. Padding, system text,
role markers, assistant prefix, and special/template tokens are excluded. The mask
and pooling rule is validated by pure design-time code in `ascr.pooling`.

---

## 6. Response-strategy labeling

Each generated response is labeled with a response strategy from
[`response-strategy-taxonomy.md`](response-strategy-taxonomy.md). Labels are based
on the *meaning* of the response, not on keyword presence, and are produced under
the lexical-normalization protocol in
[`controls-and-baselines.md`](controls-and-baselines.md). Inter-rater agreement is
measured and reported; unstable or evaluator-dependent labels are a falsification
trigger.

---

## 7. Data provenance and release

- All prompts are hand-authored and reviewed; construction rules are recorded so
  the corpus is reconstructable.
- No datasets, activations, or model outputs exist in this repository yet.
  `experiments/data/` and `experiments/results/` contain only README placeholders.
- Prompt text, labels, and the frozen model revision hash will be released with the
  first data-bearing version, subject to model-license terms.

---

## 8. Concept-mention stimulus-QA protocol (strengthened in v0.1.2)

A quality-assurance protocol governs the concept-mention cells (B and D) so that
concept mention does not covary with difficulty and cell B is not more artificial or
metalinguistic than cell A. In the 2nd pass this is made **technically binding**
with two validation modes enforced in code
([`../experiments/src/ascr/schema.py`](../experiments/src/ascr/schema.py)):

- **`draft`** — incomplete QA is allowed during authoring; **no activation
  extraction is permitted**.
- **`run_ready`** — every item and every matched group must carry a complete, typed
  QA record; no run may proceed otherwise.

**Typed QA fields (run_ready).** Each item's `qa` block must contain:
`naturalness_rating` (integer 1–5), and booleans `grammatical`, `register_match`,
`domain_match`, `target_task_match`, `solvable_as_intended`,
`label_leak_free`, `no_artificial_meta_sentence`, `primary_axis_isolated`; typed
booleans `observed_task_state_present` and `observed_concept_mention_present`;
the typed mapping `non_target_axes_absent_confirmed`; plus `reviewer_id`
(non-empty), `review_timestamp` (ISO-8601), and `disposition` (`pass` / `revise` /
`discard`).

**Item pass rule.** `disposition == pass`; all quality-confirmation flags are true;
the two observed design-factor values equal the item's registered values; the
non-target-axis mapping contains exactly the required axes, all true; and
`naturalness_rating >= 4`.

**Matched-group pass rule.** All four A/B/C/D cells present; every item passes; and
the **within-group naturalness spread across A/B/C/D is at most one scale point**.

**Whole-set gate.** `ascr.schema.check_run_ready(...)` validates an entire stimulus
set and blocks a run unless every matched group is run_ready, the model revision is
frozen, the tokenizer revision is frozen, the author-approved prompt-embedding
model and revision are frozen, the layer candidate grid is frozen, the configured
sample-size floor is met, and any externally-sourced items are review-approved (see
§10). Marker masking
and synonym-based robustness are evaluated; prompt embeddings, length, and register
features are stored as baselines/covariates. Groups failing QA are `revise`d or
`discard`ed; the disposition is logged. **No activations are collected from
unreviewed groups.**

---

## 9. Modular mini-shard and smoke protocol (corrected in v0.1.2)

The pilot is executable as versioned **mini-shards**, each testing a single axis,
**explicitly as feasibility studies**, without pretending to be the full
confirmatory study. **No arbitrary success/failure thresholds are used** — in
particular, no "balanced accuracy ≥ 75 % = success", no "≤ 60 % = failure", and no
automatic "3-percentage-point" margin.

**ASCR-Mini-0** — axis: uncertainty/unanswerability. Purpose: pipeline validation,
stimulus QA, split integrity, activation extraction, variance and effect-size
estimation, and an **early** look at H1 on the uncertainty axis. Mini-0 is
explicitly **not** a confirmatory H1 test, **not** evidence for the family claim,
and **not** a falsification verdict on ASCR as a whole.

- **Sample plan (feasibility, not a power analysis):** target **≥ 40 complete
  matched groups** for Mini-0, spread as evenly as feasible across the four domains,
  with all four A/B/C/D cells per matched group.
- **After Mini-0:** effect size, variance, and CIs are reported **in full**; before
  any powered H1 pilot, a documented **power/precision analysis** is run and its
  result is **frozen in a versioned pre-data run plan** before further data
  collection. **No cherry-picking** of positive layers or domains.

**ASCR-Mini-1** — norm tension. **ASCR-Mini-2** — controllability. Same feasibility
framing.

**Holonomy exclusion.** Mini-0/1/2 collect and analyse **no** holonomy,
dialogue-loop, path-dependence, or user-signature data (amendment §4).

Each shard carries an **immutable run manifest** with: experiment ID, shard ID,
run kind, scientific-eligibility flag, prompt-set ID and version, model name,
immutable model and tokenizer revisions, prompt-embedding name and revision, chat
template, code commit, seed, decoding configuration, layer, token position,
stimulus-file hash, output directory, environment, and timestamp (validated by
`ascr.schema.RunManifest`).

**Combination rule.** Shards may be combined only if all compatibility-relevant
manifest fields are identical (`ascr.schema.manifests_compatible`). Any change to
model, prompt construction, readout, or code is recorded as a new prompt-set
version or a separate experiment. There is **no** cherry-picking or merging of only
positive shards; all run shards are reported.

### Non-scientific technical smoke runs

A technical smoke run is not a Mini shard. It must use non-registered disposable
prompts, a `DISPOSABLE_` prompt-set identifier, a non-`ASCR-Mini-` shard ID, a
smoke-specific output directory, `run_kind: technical_smoke`, and
`eligible_for_scientific_analysis: false`. Such artifacts never enter effect-size,
variance, bootstrap, power/precision, or layer-selection calculations and cannot
be cited as preliminary evidence. They are discarded or archived only as clearly
separated technical logs. Mini-0 instead uses `run_kind:
scientific_feasibility`, remains subject to every run-ready gate, and is
structurally incompatible with a smoke manifest. This repository implements the
boundary only; it performs no smoke run.

---

## 10. External-data provenance protocol (v0.1.1 amendment, 2nd pass)

Any item adapted from an external dataset, and any source collection, records a
provenance block (`ascr.schema.EXTERNAL_PROVENANCE_FIELDS`): `dataset_name`,
`version`, `split`, `original_id`, `license`, `source`, `retrieval_date`,
`original_label`, `human_reviewed_label`, `reviewer_id`, `adjustments`,
`contamination_risk`, and `decision` (`include` / `revise` / `exclude`).

Rules:

- **No external answerability/unanswerability label is used unreviewed.** Every
  label used in ASCR is confirmed by a human against the actual prompt and context.
- Borderline cases are **discarded** or separately flagged.
- Training-data overlap is documented **as far as it is publicly checkable**.
  Unknown training data is described as **unknown**, not as "contamination-free".
- **No specific contamination claim** about a named dataset or model is included
  unless verified against a primary source for the actual model and dataset used.
- License and provenance metadata must be complete **before** the dataset is
  released.

The run-ready gate rejects any externally-sourced item whose provenance is not
review-approved (`decision == include`, with a human-reviewed label and reviewer).

---

## 11. Generation determinism: temperature and seeds (v0.1.1 amendment, 2nd pass)

- **Primary text generation uses `temperature: 0`.** Per item and per intervention
  condition, the primary output is a **single deterministic generation**.
- **Generation seeds are not interpreted as independent text samples.** Seeds
  primarily affect: matched-group splits; probe initialization / solver;
  random-direction controls; the bootstrap; and possible numerical nondeterminism.
- **Hardware, deterministic backend flags, and software versions** are recorded in
  the run manifest (`ascr.schema.RunManifest.environment` / `decoding`).
- A later **sampling-robustness analysis with `temperature > 0`** would be
  **secondary** and requires a **separately frozen** config; it is not part of the
  primary analysis.
