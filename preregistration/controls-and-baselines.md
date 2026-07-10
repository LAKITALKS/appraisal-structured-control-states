# Controls and Baselines

**Status:** v0.1 preregistration draft. No data have been collected.

This document specifies (1) the mandatory lexical-geometry control, (2) the
competing explanations and baselines the ASCR representation must beat, and (3) the
intervention controls. It is binding on the analyses in
[`analysis-plan.md`](analysis-plan.md).

---

## 1. Mandatory lexical-geometry control

A recurring deflationary explanation for any "control direction" is that the
direction merely changes the probability of stereotyped output phrases — for
example:

- "I can't",
- "sorry",
- "however",
- "I am uncertain",
- standard refusal templates.

> **A direction that changes stereotyped words without changing the underlying
> response strategy does not support the control-state hypothesis.**

Required controls against this explanation:

1. **Paraphrased output strategies.** Elicit and score multiple surface
   realizations of the same strategy so that a strategy is not tied to one phrasing.
2. **Meaning-based strategy labels.** Response-strategy labels are assigned from
   the *meaning* of the response, using the rubric in
   [`response-strategy-taxonomy.md`](response-strategy-taxonomy.md), not from
   keyword matching.
3. **Lexical normalization / marker masking.** Remove or mask stereotyped lexical
   markers before evaluation, and check whether behavior changes persist after
   normalization.
4. **Alternative phrasings expressing the same strategy.** Include, for each
   strategy, distinct wordings; a genuine strategy effect should hold across them.
5. **Persistence after lexical normalization.** Report whether intervention effects
   on *strategy* survive when stereotyped markers are stripped.
6. **Matched-vocabulary prompts.** Include prompts whose vocabulary differs while
   task structure is held constant (and vice versa), to separate the vocabulary
   factor from the task-structure factor.

If an apparent effect disappears under lexical normalization, it is scored as a
lexical-geometry artifact and does **not** support the hypothesis.

---

## 2. Competing explanations and baselines

The task-state representation must provide **incremental** explanatory value over
each of the following, both individually and jointly:

- **Bag-of-words / lexical classifiers** on the prompt.
- **Sentence / prompt embeddings** (a strong non-mechanistic baseline).
- **Prompt length** (token count).
- **Token entropy** of the model's next-token distribution.
- **Generic task difficulty** (independently rated).
- **Sentiment / signed-valence baseline.**
- **Valence/arousal subspace** baseline (cf. affect-geometry work).
- **Confidence / unanswerability direction** alone.
- **A single refusal direction** alone.
- **Evaluation-awareness direction** alone.
- **Random subspaces** and **PCA subspaces** of matched dimensionality.

Reporting: for each baseline, held-out predictive performance on response strategy,
and the incremental value of adding the task-state representation on top (nested
comparison, bootstrap CI). The full ASCR account is supported only if it adds value
beyond the *strongest* of these, not merely beyond the weakest.

---

## 3. Intervention controls

For every causal claim (H3), the following controls are preregistered:

- **Activation addition** along the identified direction (sufficiency).
- **Matched-norm random-direction controls** (same norm, random direction).
- **PCA-direction controls** (same norm, a top principal component unrelated to the
  target).
- **Directional ablation / projection removal** (necessity).
- **Several intervention strengths** (dose-response).
- **Several layers.**
- **Multiple random seeds.**

The intervention effect on response strategy should be:

- **monotonic or systematically dose-dependent** where predicted,
- **strategy-specific** (targets the predicted strategy, not a generic refusal),
- **reproducible** across seeds,
- **not merely degraded fluency** and **not a generic refusal shift**.

The analysis must distinguish changes in: **wording**, **style**, **semantic
content**, and **high-level response strategy**. Only a change in high-level
response strategy — surviving lexical normalization and exceeding matched random
controls — supports the hypothesis.

### Competence preservation

Track fluency/perplexity and off-target neutral-task accuracy under every
intervention. An intervention that shifts strategy only by destroying general
linguistic competence is treated as uninformative for the hypothesis.
