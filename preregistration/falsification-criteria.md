# Falsification Criteria

**Status:** v0.1 criteria with the H1 and H2 decision rules corrected by the v0.1.2
pre-data methodological correction; no data collected.

This document lists, in advance, the conditions under which the central
interpretation is **weakened or rejected**. Committing to these before data
collection is the point of preregistration.

---

## Central interpretation

The claim under test is that a family of *task-induced, appraisal-structured latent
control representations* of the model's own task situation partially governs
response-strategy selection, and that this is not reducible to concept tracking,
simple baselines, or lexical-phrase reweighting.

## The central interpretation is weakened or rejected if any of the following hold

1. **No cross-mention task-state transfer.** Under the double-crossed LODO design,
   the upper 95% cluster-bootstrap interval of pooled out-of-fold task-state
   balanced accuracy is at or below 0.5 after all technical and QA gates pass
   (weakens H1). An interval overlapping 0.5 is indeterminate, not positive.
   Direction-specific failure blocks a bidirectional-robustness claim.
2. **No transfer.** Cross-domain transfer fails; probes trained on some domains do
   not generalize to a held-out domain (fails H2).
3. **Baselines suffice.** Lexical classifiers or simple prompt embeddings perform
   as well as the task-state representation, with no incremental value (fails H2).
   Operationally at Mini-0 scale: with
   `delta_H2 = log_loss_prompt_embedding - log_loss_hidden_state` (positive favors
   the hidden state), the **upper** 95% paired cluster-bootstrap limit of
   `delta_H2` at or below 0 weakens H2, provided the technical, QA,
   label-reliability, split-integrity, and estimability gates pass. An interval
   overlapping 0 is indeterminate, not a refutation. A `NOT_ESTIMABLE` primary
   aggregate — including a single-class inner fit or final outer fit, or no
   converged candidate — is indeterminate, never positive; response classes are
   never merged and no fold, class, domain, or direction is dropped post-data.
   Mini-0 can weaken or support only single-axis H2 **feasibility**.
4. **Subsumed by a known single factor.** Valence/arousal, confidence, generic
   difficulty, or a single refusal direction alone explains the result (fails H2).
5. **Lexical-geometry artifact.** Causal intervention changes only stereotyped
   wording and not the underlying strategy, or effects vanish under lexical
   normalization (fails the mandatory control, H3).
6. **Indistinguishable from random.** Steering effects are not distinguishable from
   matched-norm random-direction controls (fails H3 sufficiency).
7. **No necessity.** Directional ablation has no specific behavioral effect (fails
   H3 necessity).
8. **Competence destruction.** Interventions shift strategy only by degrading
   general linguistic competence (fails H3 specificity).
9. **No selective manipulability.** Candidate axes cannot be separately
   manipulated even approximately (undermines the multi-axis claim).
10. **Controllability adds nothing.** The controllability/coping axis adds no
    explanatory value beyond simpler baselines (rejects a priority sub-hypothesis).
11. **Not reproducible.** Results fail to replicate across random seeds.
12. **Unstable labels.** Pre-adjudication Cohen's kappa on the independently
    double-labeled, domain-stratified 30% complete-group subset is below 0.60, or
    fewer than two classes make it `NOT_ESTIMABLE`. The response target is then not
    sufficiently reliable: H2 and H3 inference are withheld.

## Decision discipline

- Each numbered condition maps to a preregistered metric and decision rule in
  [`analysis-plan.md`](analysis-plan.md).
- Partial outcomes are reported honestly: e.g. H1 and H2 supported but H3
  necessity not met is reported as such, and does **not** license the full claim.
- A negative result is a publishable result. If the controls defeat the
  hypothesis, that is reported plainly.

## What a rejection would and would not mean

A rejection would mean that, for the tested model, axes, and domains, the specific
ASCR conjunction is not supported. It would **not** by itself establish that no
task-induced control structure exists in any model, nor would it validate any
anthropomorphic interpretation. The non-claims in the paper and in
[`../research/novelty-statement.md`](../research/novelty-statement.md) hold
regardless of outcome.
