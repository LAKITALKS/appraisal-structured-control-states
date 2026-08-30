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
- **Multiple random seeds** (preregistered count, e.g. 5) for every probe and
  intervention; report mean and spread.
- **Bootstrap confidence intervals** use 1,000 resamples over matched groups for
  the H1/H2 feasibility analyses; the resampling unit is the complete group.
- **Nested selection:** layer and regularization are selected only from the outer
  training domains using inner matched-group folds. Outer test labels,
  activations, outputs, and outcomes are unavailable to selection.
- **Multiple-comparison correction** uses the explicit families in §9. A single
  predeclared pooled statistic is not corrected merely for being primary.
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
regularization and network layer are selected with inner group folds using only
outer-training domains: the source-concept cells of inner-training groups fit the
probe, and the opposite-concept cells of disjoint inner-validation groups score
the candidate. The selected probe is refit on all permitted outer-training groups
and evaluated once on the untouched domain. `ascr.splits` makes these boundaries
machine-checkable.

The primary H1 statistic is **balanced accuracy on pooled out-of-fold predictions
across all four domains and both directions**. AUROC is secondary. Confidence
intervals use a cluster bootstrap over matched groups. Domain- and
direction-specific results are mandatory; no favorable subset may be selected.

- **Positive feasibility:** lower 95% CI > 0.5.
- **Weakened:** upper 95% CI ≤ 0.5, conditional on passing all technical and QA
  gates.
- **Indeterminate:** CI overlaps 0.5.
- **Bidirectional robustness:** both direction-specific aggregates must support
  transfer.

Mini-0 remains a feasibility analysis, not a powered confirmatory H1 test and not
evidence for the family claim.

## 5. H2 analysis — incremental value beyond prompt representation

H2 is separate from H1. Under the **same outer groups, directions, LODO folds, and
training-only selection boundary**, compare the hidden-state classifier with one
author-approved, frozen prompt-embedding classifier. The embedding input is the
canonical user-visible prompt text; chat-template and special-token artifacts are
excluded. Model name, immutable revision, license, pooling, and input handling must
be frozen before Mini-0. No post-data model selection is permitted.

No embedding model is selected yet. The three verified candidates, recommendation,
and blocking author decision are recorded in the v0.1.2 amendment and
`experiments/configs/pilot.yaml`.

- **Primary metric:** paired held-out log-loss on the same matched groups (hidden
  state vs prompt embedding).
- **Secondary metric:** paired balanced-accuracy difference.
- **Uncertainty:** paired cluster bootstrap over held-out matched groups.
- **Interpretation:** H1 can pass while H2 fails. If hidden-state performance does
  not add to the frozen prompt representation, the incremental ASCR interpretation
  is weakened even if task state remains decodable.

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

## 9. Multiple-comparison families (v0.1.2 correction)

The inferential families are separated by hypothesis. A significant secondary
layer, position, direction, or domain result cannot replace a failed or
indeterminate primary aggregate.

1. **H1 primary aggregate:** the single pooled out-of-fold balanced-accuracy
   statistic; no FDR correction.
2. **H1 direction/domain secondary family:** 16 tests, comprising balanced
   accuracy and AUROC for each of 2 transfer directions × 4 held-out domains;
   Benjamini–Hochberg (BH).
3. **H1 layer/position sensitivity family:** BH over each member of the Cartesian
   product of the author-approved frozen layer grid, frozen position grid, and 2
   directions (balanced accuracy). The exact grid remains a blocking decision and
   must be frozen before Mini-0.
4. **H2 primary aggregate:** the single paired hidden-state-minus-prompt-embedding
   held-out-log-loss statistic; no FDR correction.
5. **H2 direction/domain secondary family:** 8 balanced-accuracy differences for
   2 directions × 4 domains; BH.
6. **H3 intervention family:** a visible decision block. Exact members require the
   later author-approved intervention layer × strength × axis grid and must be
   frozen in a separate pre-data run plan before H3.
7. **Family-structure primary family:** exactly A shared-vs-separate log-loss, B
   strategy-selectivity contrast, and C incremental response-strategy log-loss;
   BH. The substantive decision remains A ∧ B ∧ C.

The machine-readable member names and decision blocks are in
`experiments/configs/pilot.yaml`.

## 10. Pre-commitment

- Metrics, splits, seed counts, fixed correction families, and decision thresholds are
  fixed here before data collection.
- Any deviation is reported as a deviation, with rationale, in the run log of the
  first data-bearing release.
- All analysis code, seeds, and the frozen model revision hash will be released to
  make results reconstructable.
