# Preregistered Analysis Plan

**Status:** v0.1.1 pre-data amendment; no data collected. This document
fixes the analyses *before* any data exist.

Cross-references: [`hypotheses.md`](hypotheses.md),
[`experimental-design.md`](experimental-design.md),
[`controls-and-baselines.md`](controls-and-baselines.md),
[`falsification-criteria.md`](falsification-criteria.md).

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

- **Train / validation / test** splits at the level of **matched groups**, never
  individual items, so that A/B/C/D siblings never straddle a split.
- **Leave-one-domain-out** evaluation for every transfer claim.
- **Multiple random seeds** (preregistered count, e.g. 5) for every probe and
  intervention; report mean and spread.
- **Bootstrap confidence intervals** (e.g. 1000 resamples over matched groups) for
  every reported metric.
- **Multiple-comparison correction** (Benjamini–Hochberg FDR) across the family of
  probe/axis/layer tests, with the family defined in advance.
- **Seed semantics (v0.1.1, 2nd pass).** Primary text generation is deterministic
  (`temperature: 0`, one generation per item and intervention condition). Seeds are
  **not** independent text samples; they govern matched-group splits, probe
  initialization/solver, random-direction controls, the bootstrap, and possible
  numerical nondeterminism. Any `temperature > 0` sampling-robustness analysis is
  secondary and separately frozen (see
  [`experimental-design.md`](experimental-design.md) §11).

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

## 4. H1 analysis — task-state dissociation

- Fit two probes per axis: one for `task_state_present`, one for
  `concept_mention_present`.
- Primary contrast: held-out **balanced accuracy** for the task-state probe vs the
  concept probe, evaluated on deconfounded cells (task state present, concept
  absent = cell C; task state absent, concept present = cell B).
- Decision: H1 is supported if the task-state probe reliably exceeds the concept
  probe on the deconfounded evaluation, with bootstrap CI excluding equality after
  FDR correction. H1 is weakened/rejected under the conditions in
  [`falsification-criteria.md`](falsification-criteria.md).

### H1 prompt-embedding comparison (v0.1.1, 2nd pass — does not redefine H1)

For Mini-0/H1 we additionally report a **prompt-embedding classifier for
`task_state_present`**, using the **same matched-group splits** and the **same LODO
folds** as the hidden-state probe. We report task-state decoding from: the hidden
state; the prompt embedding; lexical / bag-of-words; and prompt length.

- The **H1 decision is unchanged**: task-state probe vs concept-mention probe on the
  deconfounded cells (above). The prompt-embedding comparison is documented as a
  **strong competing explanation** and as the **link to H2** (incremental value over
  a prompt-embedding baseline), **not** as a silent redefinition of H1. A hidden
  state that merely matches a prompt embedding does not, by itself, establish a
  task-induced internal state beyond the input's surface encoding.

## 5. H2 analysis — transfer and incremental value

- **Transfer:** train on `n-1` domains, test on the held-out domain; repeat over
  all domains. Report per-domain and pooled transfer metrics with bootstrap CIs.
- **Incremental value:** nested model comparison. Base model = all simple baselines
  in [`controls-and-baselines.md`](controls-and-baselines.md) (lexical, length,
  sentiment, valence/arousal, difficulty, confidence/unanswerability, single
  refusal direction). Full model = base + task-state representation. Report the
  improvement in held-out predictive performance and whether its CI excludes zero.
- Decision: H2 is supported if the task-state representation transfers above chance
  and above the strongest single baseline, *and* adds incremental value.

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
- **Decision (A):** the **paired matched-group bootstrap** of
  `log_loss_shared − log_loss_separate` must lie **entirely below zero** after the
  preregistered FDR correction. No arbitrary margin (e.g. no "3 percentage points")
  is added; the criterion is a paired CI strictly below zero. A 3-D subspace spanned
  by three axis directions is, by itself, **not** evidence of a family.

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
  **bootstrap CI of the selectivity contrast is above zero**; the direction does
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
- **Decision (C):** component C is supported **only if** the **paired bootstrap CI**
  of the improvement (base − full log-loss) lies **entirely above zero** after FDR
  correction.

**Family claim = A ∧ B ∧ C.** The full family claim is assessed only once at least
two (ideally three) axes are adequately operationalized and tested; with two axes it
remains provisional.

## 7. H4 analysis — ordered emergence (exploratory)

- Layer x position grid of probe reliability for (a) coarse pressure/relevance,
  (b) integrated multi-axis structure, (c) committed strategy.
- Report the earliest layer/position at which each becomes reliably decodable.
- Reported as exploratory regardless of outcome; no confirmatory decision rule.

## 8. Response-strategy label reliability

- Two or more independent labelers (or a preregistered labeling protocol with an
  auditable rubric) label a shared subset; report agreement (e.g. Cohen's/Fleiss'
  kappa).
- If agreement is low or labels are evaluator-dependent, the response-strategy
  target is considered unstable and H3 conclusions are withheld.

## 9. Pre-commitment

- Metrics, splits, seed counts, correction family, and decision thresholds are
  fixed here before data collection.
- Any deviation is reported as a deviation, with rationale, in the run log of the
  first data-bearing release.
- All analysis code, seeds, and the frozen model revision hash will be released to
  make results reconstructable.
