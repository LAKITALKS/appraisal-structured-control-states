# ASCR v0.1.2 Pre-Data Methodological Correction

**Amendment date:** 2026-08-30

**Status:** pre-data correction on a review branch; not merged, tagged, released,
or archived

**Author:** Lazaros Varvatis, Independent Researcher, Berlin, Germany

## 1. Status and scope

This amendment corrects the analysis design of the archived ASCR v0.1.1
preregistration before any scientific data collection. No dataset has been
constructed; no model weights have been loaded for an ASCR run; no model has been
executed; no responses or activations have been generated; and no result has been
observed. The archived v0.1.0 and v0.1.1 records remain unchanged.

The hypotheses and the core 2×2 task-state-by-concept-mention design are retained.
The correction replaces a mathematically non-identifying H1 decision statistic,
separates the H1 and H2 gates, fixes nested selection boundaries, specifies the
Layer-0 baseline, strengthens axis-isolation QA, and makes technical smoke artifacts
structurally ineligible for scientific analysis. Publicly correcting such a defect
before data collection is an intended function of preregistration.

## 2. Why the registered H1 statistic is degenerate

The four registered cells are:

| Cell | Task state | Concept mention |
| --- | ---: | ---: |
| A | 0 | 0 |
| B | 0 | 1 |
| C | 1 | 0 |
| D | 1 | 1 |

v0.1.1 designated a difference between task-state-probe and concept-mention-probe
balanced accuracy on the deconfounded subset `{B, C}` as the primary H1 contrast.
On that subset, however, the two labels are exact complements. A perfect task-state
probe can obtain balanced accuracy 1.0 against task-state labels, and a perfect
concept-mention probe can also obtain balanced accuracy 1.0 against its own labels.
Their accuracy difference is therefore zero. Two chance-level probes can likewise
produce `0.5 - 0.5 = 0`.

The old statistic is thus **mathematically degenerate for its intended purpose**:
it cannot distinguish the intended positive case from the null case. After v0.1.2,
the B/C analysis is retained only as a fully reported, non-deciding historical
diagnostic. It cannot support, weaken, or reject H1.

## 3. Replacement H1 analysis: double-crossed transfer

H1 asks whether task-state decoding transfers when concept mention changes. Its
primary feasibility analysis now crosses concept-mention transfer with matched
groups and semantic domains.

For each of four outer leave-one-domain-out (LODO) folds, both directions are run:

1. **Concept absent → concept present.** Fit on cells A/C from matched groups in the
   three outer-training domains; evaluate on cells B/D from matched groups in the
   held-out domain.
2. **Concept present → concept absent.** Fit on B/D from matched groups in the three
   outer-training domains; evaluate on A/C from matched groups in the held-out
   domain.

The whole matched group is assigned to one side of every boundary. Cell restrictions
determine which siblings are used, but unused siblings never move to the opposite
side. No `matched_group_id` may occur on both sides of an outer or inner boundary.
The planner in `ascr.splits` constructs and validates all eight outer folds.

Out-of-fold predictions from all four domains and both directions form one
predeclared pooled aggregate. The primary metric is **balanced accuracy**; AUROC is
secondary. The uncertainty unit is the matched group, and 95% confidence intervals
use a cluster bootstrap over matched groups with 1,000 resamples, fixed here before
the first run. Every direction-specific and domain-specific result is reported; no
direction or domain may be selected after inspection.

Decision rules for the primary pooled balanced accuracy are:

- **Positive feasibility:** the lower 95% cluster-bootstrap confidence limit is
  greater than 0.5.
- **Weakened:** the upper limit is at or below 0.5, provided all technical, data-QA,
  and split-integrity gates pass.
- **Indeterminate:** the interval overlaps 0.5.
- **Bidirectional robustness:** may be stated only when both mandatory
  direction-specific aggregates support transfer.

These are feasibility rules, not arbitrary 75%/60% thresholds and not a powered
confirmatory H1 test.

## 4. Nested selection boundary

For each outer domain and direction, layer and logistic-regression regularization
are selected only inside the outer-training domains:

- in absent→present transfer, an inner fold fits on A/C from inner-training groups
  and validates on B/D from disjoint inner-validation groups;
- in present→absent transfer, it fits on B/D and validates on A/C;
- inner folds are split by `matched_group_id`;
- after selection, the model is refit once on all permitted outer-training groups
  and evaluated once on the untouched held-out domain.

The final test domain, its labels, activations, outputs, and outcomes are outside
the selector's input boundary. A complete layer curve may be reported only as a
secondary sensitivity analysis under its declared comparison family. A test-set
best layer cannot replace the primary training-selected result.

## 5. H1 and H2 are separate gates

H1 tests cross-mention transfer of the task-state target. H2 asks whether hidden
states add information beyond strong non-mechanistic prompt representations. A
positive H1 result does not answer H2.

The primary H2 comparator is a **frozen prompt-embedding model** evaluated on the
same outer matched groups, transfer directions, LODO folds, and training-only
selection boundaries. It receives only canonical user-visible prompt text; chat
template and special-token artifacts are excluded. The primary paired metric is
held-out log-loss, with balanced-accuracy difference secondary and a paired cluster
bootstrap over the same held-out matched groups.

No embedding model has been author-approved. Three open-weight candidates were
checked on 2026-08-30 against their official model cards:

| Candidate | License | Pre-data considerations |
| --- | --- | --- |
| [`BAAI/bge-base-en-v1.5`](https://huggingface.co/BAAI/bge-base-en-v1.5/tree/a5beb1e3e68b9ab74eb54cfd186867f64f240e1a) | MIT | English, 512 positions, 768 dimensions, documented CLS pooling; accepts the raw canonical prompt without an E5-style prefix. |
| [`intfloat/e5-base-v2`](https://huggingface.co/intfloat/e5-base-v2/tree/f52bf8ec8c7124536f0efb74aca902b2995e5bcd) | MIT | English, 512-token limit, 768 dimensions, documented mean pooling; its model card requires a `query:` prefix for feature use. |
| [`sentence-transformers/all-MiniLM-L6-v2`](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2/tree/1110a243fdf4706b3f48f1d95db1a4f5529b4d41) | Apache-2.0 | Small and locally practical, 384 dimensions, documented mean pooling; default truncation is 256 word pieces. |

`BAAI/bge-base-en-v1.5` is the current methodological recommendation because it is
MIT-licensed, locally tractable, has a documented pooling rule and 512-position
context, and does not require adding a synthetic input prefix. This is **not a
selection**. The author must approve one model, after which its exact name,
immutable revision, license, pooling rule, and input handling are frozen. Until
then, `run_ready` remains blocked.

TF-IDF/Bag-of-Words is retained. Under cross-mention transfer it is descriptive and
diagnostic, because vocabulary shift is built into the boundary; under ordinary
LODO it remains a secondary baseline with prompt length, token entropy, difficulty,
prompt embeddings, and the other registered controls.

## 6. Token position and Layer 0

A tokenizer-only inspection used two disposable strings, the official Qwen chat
template path, and the upstream repository snapshot
`a09a35458c702b33eeacc393d103063234e8bc28`. No weights or activations were loaded.
At that inspected snapshot:

- `Qwen2TokenizerFast` used right padding;
- the final non-padding index is defined as the greatest index whose attention mask
  is one, independent of padding side;
- with `add_generation_prompt=True`, the final token was token ID 198 (newline),
  part of the assistant-generation template after `<|im_start|>assistant`;
- the final four tokens were identical across the two disposable prompts;
- padding, system text, role markers, assistant prefix, and special tokens are not
  user content.

The binding run tokenizer revision is still unresolved and remains a blocking
sentinel. The inspection is implementation provenance, not ASCR evidence.

Hidden transformer layers retain the final non-padding prompt-token readout. At
Layer 0, the identical assistant-prefix final-token embedding is only a sanity
check. The informative baseline is the mean of embeddings whose mask is exactly
`user_content AND attention_mask AND NOT special_token`. This excludes padding,
system and role/template spans, the assistant-generation prefix, and tokenizer
special tokens. Pure mask and pooling functions plus known-sequence tests enforce
this rule.

## 7. Technical smoke boundary

The schema distinguishes two run kinds:

- `technical_smoke`: disposable, non-registered prompts; a `DISPOSABLE_` prompt-set
  identifier; a non-Mini shard ID; a smoke-specific output directory; and
  `eligible_for_scientific_analysis: false`.
- `scientific_feasibility`: a registered ASCR-Mini shard and
  `eligible_for_scientific_analysis: true`, subject to all `run_ready` gates.

Run kind, eligibility, prompt-set identity, revisions, template, code, readout, and
environment are manifest compatibility fields. Smoke and Mini-0 manifests are
therefore structurally incompatible. Smoke artifacts never enter effect-size,
variance, bootstrap, power/precision, or layer-selection calculations and cannot
be cited as preliminary evidence. They are discarded or retained only as clearly
separated technical logs. No smoke or scientific run is executed by this amendment.

## 8. Axis-isolation QA correction

The generic v0.1.1 `primary_axis_isolated` flag was not sufficient to audit the
documented requirement. v0.1.2 keeps it and adds the smallest explicit typed design:

- `observed_task_state_present` must equal the item's registered value (false in
  A/B and true in C/D);
- `observed_concept_mention_present` must equal the item's registered value;
- `non_target_axes_absent_confirmed` must contain exactly the other two primary
  axes for a primary-axis item, each mapped to `true`.

This does not incorrectly require the target state to be absent in C/D. Historical
partial v0.1.1 QA remains readable in `draft` mode but cannot pass a v0.1.2
`run_ready` validation.

## 9. Multiple-comparison families

H1, H2, H3, and family structure are separate inferential families:

- The single predeclared pooled H1 balanced-accuracy statistic is not FDR-corrected.
- The H1 secondary direction-by-domain family contains exactly 16 members: balanced
  accuracy and AUROC for 2 directions × 4 domains. Benjamini–Hochberg (BH) applies.
- The H1 layer/position family uses BH, but its exact members remain blocked until
  the layer/position grid is author-approved and frozen before Mini-0.
- The single paired aggregate H2 held-out-log-loss comparison is not FDR-corrected.
- The H2 secondary family contains the 8 balanced-accuracy differences for 2
  directions × 4 domains, corrected with BH.
- The H3 family remains a visible decision block until the intervention
  layer/strength/axis grid is frozen in its own pre-data run plan.
- The family-structure family contains exactly components A, B, and C, with BH;
  the substantive family decision remains **A ∧ B ∧ C**.

No secondary layer, position, domain, or direction result can substitute for a
failed or indeterminate primary aggregate.

## 10. Metadata and historical records

Repository version fields are advanced to `0.1.2` on this branch. The top-level CFF
artifact type is corrected to `software`, while the preferred citation remains a
report. No v0.1.2 release date or DOI is recorded because no release or archive
exists. Historical identifiers remain:

- concept DOI: `10.5281/zenodo.21294932`;
- v0.1.0 version DOI: `10.5281/zenodo.21294933`;
- v0.1.1 version DOI: `10.5281/zenodo.21335529`.

For a future Zenodo version, the intended related-resource direction is: **the
preprint is supplemented by the GitHub software**. The current `.zenodo.json`
schema does not encode that relation here; it is recorded as a manual Zenodo
metadata check rather than represented with invented syntax. No ORCID is added.

## 11. Unchanged commitments

The central hypothesis, H1–H4 statements, three primary axes, four domains,
response-strategy taxonomy, direction-derivation rule, lexical-geometry controls,
competence controls, and family decision `A ∧ B ∧ C` remain. This amendment adds no
H5, holonomy, LEM, dialogue-loop, path-dependence, or user-signature construct.

## 12. Remaining author decisions before any scientific run

1. Approve one prompt-embedding model and freeze its immutable revision, license,
   pooling, and canonical-input rule.
2. Freeze the primary model and tokenizer revisions.
3. Freeze the Mini-0 layer candidate grid and thereby the exact H1 layer/position
   sensitivity family.
4. Later, before H3, freeze the exact intervention layer/strength/axis FDR family.

The committed Mini-0 run-plan template contains blocking sentinels for these
decisions. It is not an authorization to run.
