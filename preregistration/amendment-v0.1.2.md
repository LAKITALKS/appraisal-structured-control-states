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

A focused second correction pass, prompted by an independent read-only scientific,
statistical, technical, and PDF audit of this branch, closes the remaining pre-data
specification gaps. It binds the H2 target, estimand, sign convention, and decision
rule (§5); freezes the primary probe pipeline, regularization grid, and selection
tie-breaking (§6); fixes seed roles (§7); states the cluster-bootstrap algorithm
exactly (§8); makes Benjamini–Hochberg operational rather than nominal (§9);
replaces mixed-domain inner folds with inner leave-one-training-domain-out (§4);
tightens the manifest and run-readiness guards (§11); and establishes exactly one
canonical release PDF build (§14). This is a specification pass, not a redesign:
no hypothesis, axis, domain, cell, taxonomy, or family commitment changes.

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
groups and semantic domains. The H1 target is `task_state_present`.

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
secondary. The classifier is the frozen pipeline of §6, fitted at the layer and
regularization strength selected under §4 and §6. The uncertainty unit is the
matched group, and 95% confidence intervals use the cluster bootstrap specified
exactly in §8. Every direction-specific and domain-specific result is reported; no
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

## 4. Nested selection boundary: inner leave-one-training-domain-out

For each outer domain and direction, layer and logistic-regression regularization
are selected only inside the outer-training domains. The v0.1.2 first pass used a
round-robin allocation of outer-training matched groups to inner folds, which mixed
domains inside each inner fold and therefore did not mirror the outer cross-domain
claim. This pass replaces it with **deterministic inner leave-one-training-domain-out
(inner LODO)**.

For each outer LODO fold:

- exactly three outer-training domains remain;
- each inner fold holds out one of those three domains for validation;
- the other two domains form the inner fit set;
- whole matched groups remain disjoint;
- the concept-transfer direction remains crossed — source-concept cells in the two
  inner-fit domains fit the classifier, and opposite-concept cells in the held-out
  inner-validation domain score the candidate;
- no outer-test-domain group or item enters inner selection.

This yields exactly **three deterministic inner folds** per outer fold and per
direction. Inner fold assignment does not depend on any seed. After selection, the
model is refit once on all permitted outer-training groups and evaluated once on the
untouched held-out domain.

The final test domain, its labels, activations, outputs, and outcomes are outside
the selector's input boundary. A complete layer curve may be reported only as a
secondary sensitivity analysis under its declared comparison family. A test-set
best layer cannot replace the primary training-selected result. The planner and its
validators are in `ascr.splits` (`plan_inner_selection_folds`,
`InnerSelectionFold`).

## 5. H1 and H2 are separate gates

H1 tests cross-mention transfer of the task-state target. H2 asks whether hidden
states add information beyond a strong non-mechanistic representation of the prompt.
A positive H1 result does not answer H2. **H2 is not a second task-state
classification test.**

### 5.1 Primary H2 target

The primary H2 target is the model's realized **response strategy**, represented by
the four registered response-strategy superclasses. The class vocabulary is fixed:

- `direct_or_comply`
- `qualify_or_warn`
- `redirect_or_clarify`
- `decline_or_abstain`

The nine fine-grained strategy labels remain secondary. Response-strategy labels
come from the already registered meaning-based labeling protocol in
[`response-strategy-taxonomy.md`](response-strategy-taxonomy.md), not from keyword
matching. **H2 inference is withheld if the registered response-label reliability
gate does not pass** ([`analysis-plan.md`](analysis-plan.md) §8).

The hidden-state classifier and the prompt-embedding classifier must predict
**exactly the same target on exactly the same held-out items**.

### 5.2 H2 split and selection boundary

H2 uses the same outer matched groups, the same concept-transfer directions, the
same four LODO folds, the same outer test items, and the same training-only
selection boundary as H1 (§3, §4). On the same inner folds, target, items, and
response-strategy log-loss objective, the hidden-state classifier independently
selects `(layer, C)`, while the prompt-embedding classifier independently selects
its own `C`. The smaller-`C` tie-break is applied separately; the earlier-layer
tie-break applies only to hidden states. Selection uses outer-training data only and
must never use outer-test response labels, predictions, or outcomes.

The prompt-embedding comparator receives only canonical user-visible prompt text;
chat template and special-token artifacts are excluded. It remains blocked until the
author freezes one model, its immutable revision, its license, its pooling rule, its
truncation/input rule, and its maximum input length.

### 5.3 Exact H2 estimand and decision rule

The paired primary improvement is

```
delta_H2 = log_loss_prompt_embedding - log_loss_hidden_state
```

so **positive values favor the hidden-state representation**. The same sign
convention is used in prose, in `experiments/configs/pilot.yaml`, in the tests, and
in every future result-field name.

Using a paired cluster bootstrap over the same complete held-out matched groups
(§8):

- **Positive H2 feasibility:** the lower 95% confidence limit of `delta_H2` is
  greater than 0.
- **Weakened / no incremental evidence:** the upper 95% confidence limit is at or
  below 0, provided the technical, QA, label-reliability, split-integrity, and
  estimability gates pass.
- **Indeterminate:** the interval overlaps 0.

The balanced-accuracy difference remains secondary and uses the same sign
convention: **hidden state minus prompt embedding**.

### 5.4 Estimability and claim boundary

Sparse response-strategy classes are handled conservatively, and the handling is
declared before any data exist:

- evaluation always uses the fixed four-class superclass vocabulary;
- no test fold, class, domain, or direction may be dropped after outputs are
  observed;
- response classes may never be merged post-data;
- if any inner-fit subset has only one superclass, the affected outer fold is
  `NOT_ESTIMABLE`; the same applies if the final outer fit is single-class;
- a convergence failure invalidates that candidate; an unconverged model may never
  score a validation or test fold, and if no candidate converges the affected outer
  fold is `NOT_ESTIMABLE`;
- any required `NOT_ESTIMABLE` outer fold makes the primary aggregate
  **indeterminate, not positive**;
- if a response class occurs in outer test data but not in outer training data, it
  is reported explicitly as an **unseen-class generalization failure**, and the
  returned probability columns are first aligned to the fixed class order above,
  with probability zero inserted for classes unseen in training; only then is the
  same float64 rule applied to both classifiers: clip to `[1e-15, 1 - 1e-15]` and
  renormalize over the four classes;
- affected observations are never silently excluded.

**Claim boundary.** Mini-0 can provide only **H2 feasibility on one axis** against
the frozen prompt-embedding comparator. It cannot establish full H2 and it cannot
establish the ASCR family claim. Full H2 still requires the registered stronger
baseline battery ([`controls-and-baselines.md`](controls-and-baselines.md)) and
adequately powered multi-axis evidence.

### 5.5 Response-label reliability gate

The primary human labels every generated response. Before response labels are
observed, a second independent human is assigned a deterministic, domain-stratified
subset of `ceil(0.30 × N_complete_groups)` complete matched groups, allocated as
evenly as possible across domains with seed `20260901`. Both use the fixed four-class
rubric independently. Before adjudication, report Cohen's kappa (primary), raw
agreement, the four-class confusion matrix, per-labeler class counts, and a 95%
matched-group cluster-bootstrap interval for kappa. The gate passes only if
`kappa >= 0.60`; fewer than two observed classes is `NOT_ESTIMABLE` and fails.
Adjudication may occur only afterwards, with adjudicator and rule recorded. Failure
or non-estimability withholds both H2 and H3 inference.

### 5.6 Candidate prompt-embedding models (unresolved author decision)

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
immutable revision, license, pooling rule, truncation/input rule, and maximum input
length are frozen. Until then, `run_ready` remains blocked.

TF-IDF/Bag-of-Words is retained. Under cross-mention transfer it is descriptive and
diagnostic, because vocabulary shift is built into the boundary; under ordinary
LODO it remains a secondary baseline with prompt length, token entropy, difficulty,
prompt embeddings, and the other registered controls.

## 6. Frozen primary probe specification

These design-time choices are frozen now so that they cannot be selected after data
inspection.

### 6.1 Primary logistic-regression pipeline

For the H1 and H2 primary classifiers, the registered training-only pipeline is
equivalent to:

- `StandardScaler`, fitted **only** on the relevant training subset;
- logistic regression;
- L2 penalty;
- `solver="lbfgs"`;
- `fit_intercept=True`;
- `class_weight=None`;
- `max_iter=5000`;
- `tol=1e-6`;
- float64 analysis;
- the exact scikit-learn version recorded in the future run environment.

The frozen regularization grid is

```
C ∈ {1e-4, 1e-3, 1e-2, 1e-1, 1, 10, 100}
```

and it may not be changed or selected after data exist.

Prompt embeddings retain their model-card-defined pooling and normalization
**before** the training-only classifier pipeline. The order is exactly:
model-card pooling → model-card normalization → `StandardScaler` (training-subset
only) → logistic regression.

TF-IDF and other sparse baselines may use an appropriate sparse-safe pipeline (no
dense mean-centering), but they remain **secondary** and must not silently inherit
dense centering.

### 6.2 Hyperparameter objectives and tie-breaking

- **H1 inner selection objective:** highest pooled inner-validation balanced
  accuracy across all inner folds.
- **H2 inner selection objective:** lowest pooled inner-validation
  response-strategy log-loss.
- **First tie-break:** smaller `C` (stronger regularization).
- **Second tie-break for hidden states:** earlier layer index.
- One deterministic numerical tie tolerance is used, recorded as
  `analysis.hyperparameter_selection.numerical_tie_tolerance = 1e-12` in
  `experiments/configs/pilot.yaml` and asserted by the unit tests. Two objective
  values differing by at most this tolerance are treated as tied.

The author-approved **layer candidate grid remains an unresolved, visible run
blocker**; it is not chosen in this correction pass.

### 6.3 Where selection may look

Selection consumes only outer-training-domain data, through the inner LODO folds of
§4. Outer test labels, activations, predictions, and outcomes are outside the
selector's input boundary for both H1 and H2.

## 7. Seed semantics

The earlier open-ended “several random seeds” phrasing, which named no binding count or role, is removed. The frozen roles are:

- **primary analysis seed:** `0`;
- **sensitivity seeds:** `[1, 2, 3, 4]`;
- **bootstrap seed:** `20260830`;
- **permutation seed:** `20260831`.

Binding rules:

- only seed-0 out-of-fold predictions produce the primary H1/H2 decision statistics;
- sensitivity seeds are reported separately and cannot replace the primary result;
- predictions are never pooled across seeds;
- seeds are not independent scientific samples;
- outer and inner LODO assignments are deterministic and do **not** vary by seed;
- a deterministic solver is not described as producing independent results merely
  because `random_state` changes.

## 8. Cluster bootstrap

For the H1 and H2 Mini-0 feasibility intervals:

- 1,000 bootstrap resamples are retained;
- complete `matched_group_id` clusters are resampled **with replacement**;
- resampling is stratified **within each held-out domain**, preserving the number of
  groups each domain contributed to the observed aggregate;
- all relevant predictions and items of a selected matched group are carried
  together;
- for the pooled bidirectional H1 aggregate, each held-out group carries its **four**
  out-of-fold cell predictions (cells B/D in the absent→present direction and cells
  A/C in the present→absent direction);
- for H2, the paired hidden-state and prompt-embedding losses of a group are
  resampled **together**;
- the interval is the **percentile** interval at 2.5% and 97.5%;
- the frozen bootstrap seed is used;
- individual items, cells, directions, and seeds are never bootstrapped as if
  independent.

The procedure is bound in prose here, in machine-readable form under
`analysis.bootstrap` in `experiments/configs/pilot.yaml`, and in the design-time
planner `ascr.splits.plan_cluster_bootstrap`, which returns only which matched-group
clusters a replicate would draw. The planner computes no statistic, touches no model
output, and fabricates no prediction.

## 9. Operational false-discovery-rate control

v0.1.2's first pass named Benjamini–Hochberg (BH) families but did not state how raw
p-values are produced. BH cannot be applied to ordinary unadjusted confidence
intervals. This pass makes the procedure operational without changing the family
memberships already registered in §13.

### 9.1 General rule

- BH false-discovery rate `q = 0.05`.
- BH operates on **preregistered one-sided raw p-values**.
- Raw effect estimates and raw confidence intervals are reported **separately** from
  BH-adjusted q-values.
- An ordinary confidence interval is never described as "FDR-corrected".
- No secondary result can replace a failed or indeterminate primary aggregate.

### 9.2 H1 secondary raw p-values

For fixed outer-test out-of-fold prediction scores, a **matched-group-aware
randomization test** produces the raw p-values:

- domains, matched groups, cells, directions, and prediction scores are preserved;
- under the null, the task-state labels are swapped **within the task-state pair of
  each complete matched group** — cells B/D at concept-present, cells A/C at
  concept-absent;
- one swap indicator is drawn per matched group per replicate, and the **same
  group-level swap is applied consistently to the relevant paired cells**, so the
  pooled, direction-specific, and domain-specific statistics share one group-level
  randomization;
- the pooled statistic uses all held-out groups in both directions; a
  direction-specific statistic uses the groups contributing to that direction; a
  domain-specific statistic uses the groups of that held-out domain;
- the specified balanced-accuracy or AUROC statistic is recomputed on each
  replicate;
- 10,000 random permutations are used, with the standard `+1` numerator/denominator
  correction:
  `p = (1 + #{null statistic ≥ observed statistic}) / (1 + 10000)`;
- the frozen permutation seed is used;
- the resulting one-sided raw p-values (direction of benefit: statistic above the
  chance value 0.5) are fed to BH within the already declared 16-member family.

### 9.3 H2 secondary raw p-values

For the paired hidden-state versus prompt-embedding comparisons:

- held-out items and their response-strategy superclass labels stay fixed;
- under the null, the two models' prediction blocks are exchanged at
  **matched-group** level, one exchange indicator per group per replicate;
- 10,000 random permutations are used with the same `+1` correction and the frozen
  permutation seed;
- the preregistered direction of benefit is hidden state better than prompt
  embedding, matching the §5.3 sign convention;
- the eight secondary raw p-values are fed to BH.

### 9.4 Future families and the historical v0.1.1 wording

For the future family-structure components A/B/C and for H3, no claim is made that a
confidence interval has already been FDR-corrected. Their future run plans **must
define valid component-level one-sided raw p-values before BH can be executed**, and
those grids remain blocked.

The archived v0.1.1 amendment states that each component's paired bootstrap interval
must lie entirely beyond zero "after FDR". That historical text is **preserved
unchanged**; it is a binding v0.1.1 commitment and is not rewritten. It conflicts
with the mathematics only in wording: a percentile bootstrap interval is not itself a
BH-adjustable quantity. v0.1.2 therefore implements the narrowest defensible
clarification: **both** conditions must hold — the paired bootstrap interval,
reported raw, must lie entirely beyond zero in the preregistered direction, **and**
the component's BH-adjusted one-sided raw p-value must satisfy `q = 0.05` once a
future run plan defines that p-value. Neither condition is renamed as the other, and
neither is dropped.

## 10. Token position and Layer 0

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

## 11. Technical smoke boundary and manifest guards

The schema distinguishes two run kinds:

- `technical_smoke`: disposable, non-registered prompts; a `DISPOSABLE_` prompt-set
  identifier; a non-Mini shard ID; a smoke-specific output directory; and
  `eligible_for_scientific_analysis: false`.
- `scientific_feasibility`: a registered ASCR-Mini shard and
  `eligible_for_scientific_analysis: true`, subject to all `run_ready` gates.

Manifest compatibility fields are: experiment ID, run kind, eligibility, target
axis, prompt-set identity and version, canonical stimulus hash, model name, model
revision, tokenizer revision, prompt-embedding model/revision/license/pooling/
truncation/maximum length, chat-template identity and hash, code commit, decoding
configuration, layer, token position, and environment. Each name appears exactly
once. Per-run timestamp, output directory, shard identity, and seed remain
intentionally excluded, because shard combination ranges over exactly those. Smoke
and Mini-0 manifests are therefore structurally incompatible.

Additional guards fixed in this pass:

- a scientific run requires **full immutable hexadecimal commit revisions** (40
  lowercase hex characters) for the model revision, the tokenizer revision, the
  prompt-embedding revision, and the repository code commit — never a short prefix,
  a branch, or a movable tag;
- stimulus and chat-template SHA-256 fields are validated against the explicit
  `sha256:<64 lowercase hex>` format; the stimulus digest covers the canonical,
  order-independent complete typed-item payload;
- for `technical_smoke`, prompt-embedding fields may be recorded explicitly as
  `NOT_APPLICABLE_TECHNICAL_SMOKE` when no prompt-embedding model is used, so that a
  non-scientific extraction smoke test never has to invent a fake frozen embedding
  revision;
- for `scientific_feasibility`, all prompt-embedding fields remain mandatory and
  frozen, and the not-applicable sentinel is rejected;
- the current helpers are **design-time guards**. The future extraction runner must
  call the four-artifact gate
  `integrated_pre_run_gate_problems(config, items, run_plan=plan,
  manifest=manifest)` and find it empty **before** model construction. A config-only
  helper can never authorize a scientific run. Mini-0 does not depend on the later
  H3 grid; that separate gate becomes binding only before H3.

Smoke artifacts never enter effect-size, variance, bootstrap, power/precision, or
layer-selection calculations and cannot be cited as preliminary evidence. They are
discarded or retained only as clearly separated technical logs. No smoke or
scientific run is executed by this amendment.

## 12. Axis-isolation QA correction

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

## 13. Multiple-comparison families

H1, H2, H3, and family structure are separate inferential families. The BH procedure
that operates on them is specified in §9.

- The single predeclared pooled H1 balanced-accuracy statistic is not FDR-corrected.
- The H1 secondary direction-by-domain family contains exactly 16 members: balanced
  accuracy and AUROC for 2 directions × 4 domains. BH applies to the one-sided raw
  p-values of §9.2.
- The H1 layer/position family uses BH, but its exact members and its raw-p-value
  procedure remain blocked until the layer/position grid is author-approved and
  frozen before Mini-0.
- The single paired aggregate H2 held-out-log-loss comparison (`delta_H2`, §5.3) is
  not FDR-corrected.
- The H2 secondary family contains the 8 balanced-accuracy differences for 2
  directions × 4 domains, corrected with BH over the one-sided raw p-values of §9.3.
- The H3 family remains a visible decision block until the intervention
  layer/strength/axis grid and its raw-p-value procedure are frozen in their own
  pre-data run plan.
- The family-structure family contains exactly components A, B, and C, with BH; the
  substantive family decision remains **A ∧ B ∧ C**, under the clarification in §9.4.

No secondary layer, position, domain, or direction result can substitute for a
failed or indeterminate primary aggregate.

## 14. Canonical release build

The independent audit reproduced the committed Tectonic PDF hash but found that the
previous `make paper` preferred `latexmk` when available and then produced a
different valid PDF with a different SHA-256. A build that can silently switch
engines cannot define an archival artifact.

Exactly one canonical release build is now defined:

- **canonical engine:** Tectonic 0.16.9, `-Z deterministic-mode`, with
  `SOURCE_DATE_EPOCH` fixed to midnight UTC on the amendment date (1788048000);
- `make paper` and its clearly named alias `make paper-release` use that engine and
  nothing else; there is **no engine fallback**;
- a missing canonical engine, or a version mismatch, fails loudly instead of
  silently producing a different archival artifact;
- `latexmk` remains available only as `make paper-dev`, explicitly labelled a
  **noncanonical development build** whose output must never be committed as
  `paper/preprint.pdf` or released;
- `make paper-verify` builds twice from a clean build-artifact state and requires
  byte-identical output;
- no byte identity is claimed across different engines.

`paper/preprint.pdf` remains a **local review artifact**, not an archived
publication. It carries no DOI and no release date, because neither exists.

## 15. Metadata and historical records

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

v0.1.2 is **not** a non-substantive metadata release. It is an explicit pre-data
methodological correction.

## 16. Unchanged commitments

The central hypothesis, H1–H4 statements, three primary axes, four domains,
response-strategy taxonomy, direction-derivation rule, lexical-geometry controls,
competence controls, and family decision `A ∧ B ∧ C` remain. This amendment adds no
H5, holonomy, LEM, dialogue-loop, path-dependence, or user-signature construct.

## 17. Remaining author decisions before any scientific run

1. Approve one prompt-embedding model and freeze its immutable revision, license,
   pooling rule, truncation/input rule, and maximum input length.
2. Freeze the primary Qwen model revision.
3. Freeze the tokenizer revision.
4. Freeze the primary layer candidate grid.
5. Freeze the exact position-sensitivity grid, and thereby the exact H1
   layer/position sensitivity family and its raw-p-value procedure.
6. Later, before H3, freeze the exact intervention layer/strength/axis FDR family
   and its raw-p-value procedure.

The following are **no longer open**: the H2 primary target and class vocabulary,
the H2 log-loss sign convention, the H2 positive/weakened/indeterminate rules, the
logistic-regression pipeline and solver, the regularization `C` grid, the inner
selection objectives and tie-breaking, the inner leave-one-training-domain-out
structure, the seed roles, the cluster-bootstrap algorithm, and the BH raw-p-value
procedures for the H1 and H2 secondary families.

The committed Mini-0 run-plan template contains blocking sentinels for the remaining
decisions. It is not an authorization to run.
