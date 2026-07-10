# Preregistered Analysis Plan

**Status:** v0.1 preregistration draft. No data have been collected. This document
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
