# Preregistered Analysis Plan

**Status:** v0.1.2 pre-data methodological correction; no data collected. This
document fixes the analyses *before* any data exist.

Cross-references: [`hypotheses.md`](hypotheses.md),
[`experimental-design.md`](experimental-design.md),
[`controls-and-baselines.md`](controls-and-baselines.md),
[`falsification-criteria.md`](falsification-criteria.md), and
[`amendment-v0.1.2.md`](amendment-v0.1.2.md).

---

## 1. Probing methods (simple and interpretable first)

Primary decoders, in order of preference:

- **Logistic regression** for categorical targets (task-state factor, concept
  factor, response strategy).
- **Ridge regression** for graded targets (e.g. graded controllability).
- **Linear discriminant analysis** where a low-dimensional discriminative subspace
  is wanted.

Nonlinear probes (e.g. small MLPs) are reported only as a secondary robustness
check and never as the primary evidence, because a powerful probe can recover
information that the model does not use.

## 2. Splits, seeds, and uncertainty

- **Train / validation / test** assignments are made at the level of **whole
  matched groups**, never individual items. Cell restrictions select siblings for
  a particular fit, but unused siblings never migrate to the opposite side.
- **Leave-one-domain-out** evaluation for every transfer claim.
- **Nested selection:** layer and regularization are selected only from the outer
  training domains, using **inner leave-one-training-domain-out** folds (§2a).
  Outer test labels, activations, outputs, and outcomes are unavailable to
  selection.
- **Bootstrap confidence intervals** use the domain-stratified matched-group
  cluster bootstrap specified exactly in §2c.
- **Multiple-comparison correction** uses the explicit families in §9 and the
  operational Benjamini–Hochberg procedure in §9a. A single predeclared pooled
  statistic is not corrected merely for being primary.
- **Seed semantics (v0.1.1, 2nd pass; roles frozen in v0.1.2).** Primary text
  generation is deterministic (`temperature: 0`, one generation per item and
  intervention condition). Seeds are **not** independent text samples; they govern
  probe initialization/solver, random-direction controls, the bootstrap, and
  possible numerical nondeterminism. Any `temperature > 0` sampling-robustness
  analysis is secondary and separately frozen (see
  [`experimental-design.md`](experimental-design.md) §11).

### Frozen seed roles (v0.1.2)

The earlier open-ended “several random seeds” phrasing, which named no binding count or role, is removed. The roles are fixed:

| Role | Value |
| --- | --- |
| Primary analysis seed | `0` |
| Sensitivity seeds | `[1, 2, 3, 4]` |
| Bootstrap seed | `20260830` |
| Permutation seed | `20260831` |

- Only **seed-0** out-of-fold predictions produce the primary H1/H2 decision
  statistics.
- Sensitivity seeds are reported separately and **cannot replace** the primary
  result.
- Predictions are **never pooled** across seeds.
- Seeds are **not** independent scientific samples.
- Outer and inner LODO assignments are deterministic and do **not** vary by seed.
- A deterministic solver is not described as producing independent results merely
  because `random_state` changes.

## 2a. Inner leave-one-training-domain-out selection (v0.1.2 correction)

Inner selection folds are no longer a round-robin allocation of outer-training
matched groups, which mixed domains inside each inner fold. For each outer LODO
fold and each transfer direction:

- exactly three outer-training domains remain;
- each inner fold holds out **one** of those three domains for validation;
- the other **two** domains form the inner fit set;
- whole matched groups remain disjoint;
- the concept-transfer direction stays crossed — source-concept cells of the two
  inner-fit domains fit the candidate, opposite-concept cells of the held-out
  inner-validation domain score it;
- no outer-test-domain group or item enters inner selection.

This produces exactly **three deterministic inner folds** per outer fold and
direction, and mirrors the outer cross-domain claim more closely than mixed-domain
folds. `ascr.splits.plan_inner_selection_folds` constructs and validates them.

## 2b. Frozen primary probe pipeline (v0.1.2)

The primary H1 and H2 classifiers use one frozen training-only pipeline:

- `StandardScaler`, fitted **only** on the relevant training subset;
- logistic regression, L2 penalty, `solver="lbfgs"`, `fit_intercept=True`,
  `class_weight=None`, `max_iter=5000`, `tol=1e-6`;
- float64 analysis; the exact scikit-learn version is recorded in the future run
  environment;
- frozen regularization grid `C ∈ {1e-4, 1e-3, 1e-2, 1e-1, 1, 10, 100}`, which may
  not be changed or selected after data exist.

Prompt embeddings keep their model-card-defined pooling and normalization
**before** this pipeline: model-card pooling → model-card normalization →
`StandardScaler` (training subset only) → logistic regression. TF-IDF and other
sparse baselines may use a sparse-safe pipeline without dense mean-centering, but
they remain **secondary** and never silently inherit dense centering.

**Selection objectives and tie-breaking.** H1 selects on the highest pooled
inner-validation balanced accuracy across all inner folds. For H2, on the same
inner folds, target, items, and lowest pooled response-strategy log-loss objective,
the hidden-state model independently selects `(layer, C)` and the prompt-embedding
model independently selects its own `C`. The smaller-`C` tie-break is applied
separately to each classifier; the earlier-layer tie-break applies only to hidden
states. One deterministic numerical tie tolerance (`1e-12`) is recorded in
`experiments/configs/pilot.yaml` and asserted by the tests. The author-approved
**layer candidate grid remains a visible Mini-0 run blocker**.

## 2c. Cluster bootstrap (frozen algorithm, v0.1.2)

For the H1 and H2 Mini-0 feasibility intervals:

- 1,000 resamples;
- complete `matched_group_id` clusters resampled **with replacement**;
- resampling **stratified within each held-out domain**, preserving the number of
  groups each domain contributed to the observed aggregate;
- every prediction and item of a drawn group travels with it;
- for the pooled bidirectional H1 aggregate, each held-out group carries its
  **four** out-of-fold cell predictions (B/D in absent→present, A/C in
  present→absent);
- for H2, the paired hidden-state and prompt-embedding losses of a group are
  resampled **together**;
- **percentile** interval at 2.5% and 97.5%;
- the frozen bootstrap seed `20260830`;
- individual items, cells, directions, and seeds are **never** bootstrapped as if
  independent.

The machine-readable form is `analysis.bootstrap` in
`experiments/configs/pilot.yaml`; the design-time planner
`ascr.splits.plan_cluster_bootstrap` returns only which matched-group clusters a
replicate would draw and computes no statistic.

## 3. Identifiability, not orthogonality

We characterize the candidate control coordinates as:

- **separately decodable**,
- **cross-domain transferable**,
- **interventionally identifiable**,
- **incrementally predictive**,
- **selectively manipulable**.

We explicitly do **not** require the axes to be *mutually independent*,
*structurally uncorrelated*, or *necessarily orthogonal*. Correlations between axes
are measured and reported, not assumed away. Where axes are correlated, selective
manipulability (moving one strategy-relevant axis while holding others fixed as far
as possible) is the operative criterion.

## 4. H1 analysis — double-crossed task-state transfer

The v0.1.1 B/C accuracy-difference statistic is non-identifying because task-state
and concept-mention labels are exact complements on `{B, C}`. It is fully reported
as a **non-deciding diagnostic only**; see
[`amendment-v0.1.2.md`](amendment-v0.1.2.md) §2.

The replacement primary feasibility analysis predicts `task_state_present` under
two cross-mention directions inside each outer LODO fold:

- **concept absent → present:** train on A/C from the three outer-training domains;
  test on B/D from the held-out domain;
- **concept present → absent:** train on B/D from the three outer-training domains;
  test on A/C from the held-out domain.

All four domains serve once as the outer test domain. Whole matched groups stay on
one side of each boundary. For every outer fold and direction, logistic
regularization and network layer are selected with the inner
leave-one-training-domain-out folds of §2a, using only outer-training domains: the
source-concept cells of the two inner-fit domains fit the probe, and the
opposite-concept cells of the held-out inner-validation domain score the candidate.
Selection uses the frozen pipeline, grid, objective, and tie-breaks of §2b. The
selected probe is refit on all permitted outer-training groups and evaluated once
on the untouched domain. `ascr.splits` makes these boundaries machine-checkable.

The primary H1 statistic is **balanced accuracy on pooled out-of-fold predictions
across all four domains and both directions**, computed from **seed-0** predictions
only. AUROC is secondary. Confidence intervals use the domain-stratified
matched-group cluster bootstrap of §2c. Domain- and direction-specific results are
mandatory; no favorable subset may be selected.

- **Positive feasibility:** lower 95% CI > 0.5.
- **Weakened:** upper 95% CI ≤ 0.5, conditional on passing all technical and QA
  gates.
- **Indeterminate:** CI overlaps 0.5.
- **Bidirectional robustness:** both direction-specific aggregates must support
  transfer.

Mini-0 remains a feasibility analysis, not a powered confirmatory H1 test and not
evidence for the family claim.

## 5. H2 analysis — incremental value beyond prompt representation

H2 is separate from H1 and is **not** a second task-state classification test. It
asks whether hidden states incrementally predict the model's *realized response
strategy* beyond a non-mechanistic representation of the prompt.

### 5.1 Primary target

- **Primary H2 target:** the four registered response-strategy **superclasses**.
- **Fixed class vocabulary:** `direct_or_comply`, `qualify_or_warn`,
  `redirect_or_clarify`, `decline_or_abstain`.
- The nine fine-grained strategy labels remain **secondary**.
- Response-strategy labels come from the already registered meaning-based labeling
  protocol in [`response-strategy-taxonomy.md`](response-strategy-taxonomy.md).
- **H2 inference is withheld if the response-label reliability gate in §8 does not
  pass.**
- The hidden-state classifier and the prompt-embedding classifier predict **exactly
  the same target on exactly the same held-out items**.

### 5.2 Splits and selection boundary

H2 uses the **same** outer matched groups, concept-transfer directions, four LODO
folds, outer test items, and training-only selection boundary as H1 (§4, §2a). As
specified in §2b, hidden states independently select `(layer, C)` and prompt
embeddings independently select `C`, using the identical inner folds, target, items,
and pooled inner-validation response-strategy log-loss. Neither selector ever uses
outer-test response labels, predictions, or outcomes.

The prompt-embedding comparator receives only canonical user-visible prompt text;
chat-template and special-token artifacts are excluded. It stays blocked until the
author freezes one model, its immutable revision, license, pooling rule,
truncation/input rule, and maximum input length. No embedding model is selected
yet; the candidates, recommendation, and blocking author decision are recorded in
[`amendment-v0.1.2.md`](amendment-v0.1.2.md) §5.6 and
`experiments/configs/pilot.yaml`.

### 5.3 Estimand, sign convention, and decision rule

The paired primary improvement is

```
delta_H2 = log_loss_prompt_embedding - log_loss_hidden_state
```

so **positive values favor the hidden-state representation**. The identical sign
convention is used in prose, in YAML, in the tests, and in future result-field
names.

Using the paired cluster bootstrap of §2c over the same complete held-out matched
groups:

- **Positive H2 feasibility:** the lower 95% confidence limit of `delta_H2` is
  greater than 0.
- **Weakened / no incremental evidence:** the upper 95% confidence limit is at or
  below 0, provided the technical, QA, label-reliability, split-integrity, and
  estimability gates pass.
- **Indeterminate:** the interval overlaps 0.

The **secondary** metric is the paired balanced-accuracy difference with the same
sign convention: **hidden state minus prompt embedding**.

### 5.4 Estimability and claim boundary

- Evaluation always uses the fixed four-class superclass vocabulary.
- No test fold, class, domain, or direction may be dropped after outputs are
  observed.
- Response classes may never be merged post-data.
- A single-class inner-fit subset makes its affected outer fold `NOT_ESTIMABLE`;
  a single-class final outer fit does the same.
- A convergence failure invalidates that candidate. An unconverged model may never
  score validation or test data; if no candidate converges, the outer fold is
  `NOT_ESTIMABLE`.
- Any required `NOT_ESTIMABLE` outer fold makes the Mini-0 H2 aggregate
  **indeterminate, not positive**.
- If a response class occurs in outer test data but not in outer training data, it
  is reported explicitly as an **unseen-class generalization failure**, and the
  returned probability columns are aligned to the fixed class order first, inserting
  zero for every class unseen in training. The identical float64 log-loss rule is
  then applied to both classifiers: clip to `[1e-15, 1 - 1e-15]`, then renormalize
  over the four classes.
- Affected observations are never silently excluded.

**Claim boundary.** Mini-0 can provide only **H2 feasibility on one axis** against
the frozen prompt-embedding comparator. It cannot establish full H2 and it cannot
establish the ASCR family claim. Full H2 still requires the registered stronger
baseline battery in [`controls-and-baselines.md`](controls-and-baselines.md) and
adequately powered multi-axis evidence.

### 5.5 Relation to H1 and to lexical baselines

H1 can pass while H2 fails. If hidden-state performance does not add to the frozen
prompt representation, the incremental ASCR interpretation is weakened even if task
state remains decodable.

TF-IDF/Bag-of-Words remains a cross-mention diagnostic rather than the primary H2
comparator. Under ordinary LODO, it and the full registered baseline battery remain
secondary comparisons.

## 6. H3 analysis — causal intervention

- **Sufficiency:** matched-norm activation addition along the identified direction;
  measure the change in the rate of the predicted strategy vs matched-norm random
  and PCA-direction controls, across several strengths, layers, and seeds.
- **Necessity:** directional ablation / projection removal / counter-steering;
  measure reduction in the predicted strategy vs the same controls.
- **Dose response:** fit the strategy rate as a function of intervention strength;
  test for the predicted monotonic/systematic trend.
- **Specificity:** confirm the effect is on the *targeted* strategy, not a generic
  shift toward refusal, and not merely degraded fluency (see competence checks).
- **Competence preservation:** track perplexity/fluency and performance on
  off-target neutral tasks; large degradation invalidates the intervention.
- Decision rules and failure conditions in
  [`falsification-criteria.md`](falsification-criteria.md).

## 6b. Family-structure test (v0.1.1 amendment)

Preregistered addition (see [`amendment-v0.1.1.md`](amendment-v0.1.1.md) §5). The
shared-control-family claim is **not** established by H1–H3 alone: succeeding on
three individual axes is compatible with three independent, already-known
directions. This is a precommitment, not a post-hoc discovery.

> **Decision rule (binding).** The family claim is supported **only if all three
> components A, B, and C independently meet their preregistered criteria below.**
> No single advantage from any list is sufficient; A ∧ B ∧ C is required. All
> secondary metrics are reported in full but never substitute for the primary
> per-component decision.

### A. Shared low-rank model vs separate models

- **Shared model:** a common shared bottleneck `Q` (rank `r`), `z = Q^T h`, with
  **axis-specific logistic heads** `y_j = softmax(a_j^T z)`, trained multi-task.
- **Comparator:** **separate, regularized per-axis** logistic models, one per axis.
- **Splits:** identical matched-group splits for shared and separate models;
  **leave-one-domain-out (LODO)**; strictly **nested** cross-validation
  (rank and regularization chosen only in the inner training/validation loop, never
  on the outer test fold). Random-subspace and PCA controls of the same rank `r`.
- **Rank selection (fixed grid).** With **three** axes tested, the primary rank grid
  is `r ∈ {1, 2}`; `r = 3` may appear **only** as a secondary sensitivity analysis,
  because three directions trivially span an at-most-3-D space. With **two** axes
  tested, the shared-compression test with `r = 1` is admissible, but the full
  family claim remains provisional until three axes are tested.
- **Primary metric:** **pooled held-out log-loss (cross-entropy)** over axes and
  LODO folds.
- **Secondary metrics (reported, non-deciding):** macro balanced accuracy, per-axis
  balanced accuracy, subspace stability across seeds/folds, and effective model
  complexity.
- **Decision (A):** the **paired matched-group bootstrap** interval of
  `log_loss_shared − log_loss_separate`, reported **raw**, must lie **entirely below
  zero**, **and** component A's BH-adjusted one-sided raw p-value must satisfy
  `q = 0.05` once the future run plan defines that p-value (§9a.4). The interval is
  not itself "FDR-corrected". No arbitrary margin (e.g. no "3 percentage points")
  is added. A 3-D subspace spanned by three axis directions is, by itself, **not**
  evidence of a family.

### B. Structured behavioral specificity

Preregistered, falsifiable direction→strategy expectations, stated with **canonical
taxonomy terms only** (fine labels / superclasses from
[`response-strategy-taxonomy.md`](response-strategy-taxonomy.md)):

- **Uncertainty / unanswerability →** `calibrated_answer`, `hedging`,
  `clarification_request`, `abstention`.
- **Low controllability →** `clarification_request`, `conditional_continuation`,
  `abstention`.
- **Norm tension →** `warning`, `correction`, `conditional_continuation`, and
  `refusal` only where genuinely required.

Define an **intervention-effect matrix** `E[axis, response_superclass]`. For each
axis a preregistered **target set** of strategies is fixed (above). Compute a
**selectivity contrast** per axis:

```
selectivity(axis) = mean effect on preregistered target strategies
                    - mean absolute effect on off-target strategies
```

- **Decision (B):** component B is supported **only if**, for the tested axes, the
  **raw bootstrap CI of the selectivity contrast is above zero** and its
  BH-adjusted one-sided raw p-value satisfies `q = 0.05` under a future run plan
  that defines it (§9a.4); the direction does
  **not** mainly produce generic refusal, negativity, or fluency-degradation
  effects; the **competence controls pass**; and the effect **persists after lexical
  normalization**.

### C. Incremental shared contribution

Nested comparison, evaluated on held-out domains:

- **Base:** known single directions (unanswerability, refusal, difficulty where
  reproducible) plus simple baselines (see
  [`controls-and-baselines.md`](controls-and-baselines.md)).
- **Full:** base **+** the shared ASCR representation.
- **Primary metric:** **held-out response-strategy log-loss.**
- **Decision (C):** component C is supported **only if** the **raw paired bootstrap
  CI** of the improvement (base − full log-loss) lies **entirely above zero**, **and**
  component C's BH-adjusted one-sided raw p-value satisfies `q = 0.05` once the
  future run plan defines it (§9a.4).

**Family claim = A ∧ B ∧ C.** The full family claim is assessed only once at least
two (ideally three) axes are adequately operationalized and tested; with two axes it
remains provisional.

## 7. H4 analysis — ordered emergence (exploratory)

- Layer x position grid of probe reliability for (a) coarse pressure/relevance,
  (b) integrated multi-axis structure, (c) committed strategy.
- Report the earliest layer/position at which each becomes reliably decodable.
- Reported as exploratory regardless of outcome; no confirmatory decision rule.

## 8. Response-strategy label reliability

The primary human labels **all** generated responses. Before response labels are
observed, a second independent human is assigned
`ceil(0.30 × N_complete_groups)` complete matched groups. Selection is deterministic
(seed `20260901`), stratified by domain as evenly as possible, and uses prompt
metadata only. The second labeler is blind to primary labels; both independently use
the four-superclass rubric.

Reliability is computed **before adjudication**. The primary statistic is Cohen's
kappa; the gate passes only if `kappa >= 0.60`. Also report raw agreement, the
four-class confusion matrix, class counts for each labeler, and a 95% matched-group
cluster-bootstrap CI for kappa (1,000 resamples, seed `20260902`). Fewer than two
observed classes is `NOT_ESTIMABLE` and fails the gate. Only after this record is
fixed may disagreements be adjudicated; the adjudicator and rule are recorded.

Failure or non-estimability withholds **both H2 and H3 inference**. An unreliable
target cannot support either an incremental-value or intervention claim.

## 9. Multiple-comparison families (v0.1.2 correction)

The inferential families are separated by hypothesis. A significant secondary
layer, position, direction, or domain result cannot replace a failed or
indeterminate primary aggregate. The procedure that operates on these families is
specified in §9a.

1. **H1 primary aggregate:** the single pooled out-of-fold balanced-accuracy
   statistic; no FDR correction.
2. **H1 direction/domain secondary family:** 16 tests, comprising balanced
   accuracy and AUROC for each of 2 transfer directions × 4 held-out domains;
   Benjamini–Hochberg (BH) over the one-sided raw p-values of §9a.2.
3. **H1 layer/position sensitivity family:** BH over each member of the Cartesian
   product of the author-approved frozen layer grid, frozen position grid, and 2
   directions (balanced accuracy). The exact grid **and** its raw-p-value procedure
   remain blocking decisions and must be frozen before Mini-0.
4. **H2 primary aggregate:** the single paired `delta_H2` held-out-log-loss
   statistic (§5.3); no FDR correction.
5. **H2 direction/domain secondary family:** 8 balanced-accuracy differences for
   2 directions × 4 domains; BH over the one-sided raw p-values of §9a.3.
6. **H3 intervention family:** a visible decision block. Exact members and their
   raw-p-value procedure require the later author-approved intervention layer ×
   strength × axis grid and must be frozen in a separate pre-data run plan before
   H3.
7. **Family-structure primary family:** exactly A shared-vs-separate log-loss, B
   strategy-selectivity contrast, and C incremental response-strategy log-loss;
   BH. The substantive decision remains A ∧ B ∧ C, read as in §9a.4.

The machine-readable member names and decision blocks are in
`experiments/configs/pilot.yaml`.

## 9a. Operational Benjamini–Hochberg procedure (v0.1.2 correction)

Naming a BH family is not enough: BH needs raw p-values, and it cannot be applied
to ordinary unadjusted confidence intervals. The family memberships in §9 are
unchanged; what follows is how their p-values are produced.

### 9a.1 General rule

- BH false-discovery rate **`q = 0.05`**.
- BH operates on **preregistered one-sided raw p-values**.
- Raw effect estimates and raw confidence intervals are reported **separately** from
  BH-adjusted q-values.
- An ordinary confidence interval is **never** described as "FDR-corrected".
- No secondary result can replace a failed or indeterminate primary aggregate.

### 9a.2 H1 secondary raw p-values

A **matched-group-aware randomization test** on the fixed outer-test out-of-fold
prediction scores:

- domains, matched groups, cells, directions, and prediction scores are preserved;
- under the null, task-state labels are swapped **within the task-state pair of each
  complete matched group** — cells B/D at concept-present, cells A/C at
  concept-absent;
- one swap indicator is drawn per matched group per replicate, and the **same
  group-level swap is applied consistently** to that group's paired cells, so the
  pooled, direction-specific, and domain-specific statistics share one group-level
  randomization per replicate;
- **pooled** members use all held-out groups in both directions;
  **direction-specific** members use the groups contributing to that direction;
  **domain-specific** members use the groups of that held-out domain;
- the declared balanced-accuracy or AUROC statistic of the member is recomputed;
- **10,000** random permutations with the standard `+1` correction,
  `p = (1 + #{null ≥ observed}) / (1 + 10000)`;
- the frozen permutation seed `20260831`;
- the one-sided direction of benefit is the statistic **above the chance value
  0.5**;
- the resulting raw p-values are fed to BH within the 16-member family.

### 9a.3 H2 secondary raw p-values

A **paired model-block exchange permutation test**:

- held-out items and their response-strategy superclass labels stay fixed;
- under the null, the hidden-state and prompt-embedding prediction blocks of a
  complete matched group are exchanged, one exchange indicator per group per
  replicate;
- **10,000** permutations with the same `+1` correction and the frozen permutation
  seed;
- the preregistered direction of benefit is **hidden state better than prompt
  embedding**, matching the §5.3 sign convention;
- the eight resulting raw p-values are fed to BH.

### 9a.4 Future families and the historical v0.1.1 wording

For the family-structure components A/B/C and for H3, **no claim is made that a
confidence interval has already been FDR-corrected**. Their future run plans must
define valid component-level one-sided raw p-values before BH can be executed, and
those grids remain blocked.

The archived v0.1.1 amendment says each component's paired bootstrap interval must
lie entirely beyond zero "after FDR". That historical text is preserved unchanged in
[`amendment-v0.1.1.md`](amendment-v0.1.1.md); it is a binding v0.1.1 commitment and
is not rewritten. It conflicts with the mathematics only in wording, because a
percentile bootstrap interval is not itself a BH-adjustable quantity. The narrowest
defensible clarification, implemented here and in
[`amendment-v0.1.2.md`](amendment-v0.1.2.md) §9.4, is that **both** conditions must
hold: the raw paired bootstrap interval lies entirely beyond zero in the
preregistered direction, **and** the component's BH-adjusted one-sided raw p-value
satisfies `q = 0.05` once a future run plan defines that p-value. Neither condition
is renamed as the other, and neither is dropped.

## 10. Pre-commitment

- Metrics, splits, seed **roles**, the probe pipeline and regularization grid, the
  bootstrap algorithm, the fixed correction families, the raw-p-value procedures,
  and the decision rules are fixed here before data collection.
- Any deviation is reported as a deviation, with rationale, in the run log of the
  first data-bearing release.
- All analysis code, seeds, and the frozen model revision hash will be released to
  make results reconstructable.
