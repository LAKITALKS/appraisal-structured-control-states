# Controls and Baselines

**Status:** v0.1.2 pre-data methodological correction; no data collected.

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

---

## 4. Primary direction derivation (v0.1.1 amendment)

Preregistered addition (see [`amendment-v0.1.1.md`](amendment-v0.1.1.md) §6). The
v0.1.0 plan named several probes and interventions but did not fix a single primary
steering direction. To remove analytic degrees of freedom, exactly one primary rule
is fixed here; everything else is a declared robustness analysis.

1. **Primary decoding:** regularized logistic regression.
2. **Primary intervention direction:** the **normalized difference-in-means** of
   activations between task-state-present and task-state-absent, computed **only**
   from training groups, with the concept-mention factor **balanced** within the
   training data. Formally, with `mu_present` and `mu_absent` the training-group
   means at a fixed (layer, token position),
   `d = (mu_present - mu_absent) / || mu_present - mu_absent ||`.
3. **Robustness only:** probe-weight, LDA, and ridge directions are declared
   robustness analyses, never the primary result.
4. **Layer selection:** chosen using training/validation data only. The test set is
   never used to choose layer or direction.
5. **Intervention strengths:** a fixed, preregistered set of values. The best
   strength is never selected on the final test set.
6. **Normalization:** the primary direction and every control share **identical
   norm**.
7. **Named-direction controls:** matched-norm random directions, PCA directions,
   and known unanswerability / refusal / difficulty directions where these can be
   reproduced.

This supersedes the more permissive v0.1.0 phrasing (which listed logistic
regression, ridge, and LDA as co-equal candidates). The change is documented here,
in the amendment, and in the CHANGELOG; no data existed when it was made.

---

## 5. Baseline battery (H1/H2 roles corrected in v0.1.2)

The v0.1.0 baseline list (Section 2 above) is retained and refined. Two baselines
are elevated to **primary** comparisons:

- **Prompt-embedding baseline** — the primary non-mechanistic H2 comparator under
  the same double-crossed outer groups, directions, LODO folds, and training-only
  hyperparameter selection as the hidden-state probe. Its input is canonical
  user-visible prompt text, excluding chat-template/special-token artifacts. Exact
  model, immutable revision, license, pooling, and input handling must be frozen
  before Mini-0; the unresolved author decision is documented in
  [`amendment-v0.1.2.md`](amendment-v0.1.2.md). Held-out log-loss is primary and
  paired balanced-accuracy difference secondary.
- **Difficulty-representation baseline** — a decodable generic-difficulty
  representation (cf. linear difficulty probes in prior work), included because
  difficulty is a known confound for the task-state axes. Primary **where
  reproducible**; otherwise a planned robustness check (see below).

Tiering of baselines by pilot stage:

- **Mandatory in the mini-pilot (per axis):** prompt-embedding, prompt length,
  token entropy, lexical/bag-of-words, matched-norm random and PCA subspaces.
- **Added in the full pilot:** sentiment/signed-valence, valence/arousal subspace,
  confidence/unanswerability direction, single refusal direction,
  evaluation-awareness direction.
- **Planned robustness only (no reproducible code/weights):** any baseline whose
  published direction or weights cannot be reproduced is reported as a planned
  robustness comparison, clearly labeled as not-yet-run, never as a completed
  result.

Support for ASCR requires incremental value over the **strongest** primary
baseline, including the prompt-embedding and difficulty baselines, not merely over
the weakest.

### Cross-mention role of lexical baselines

TF-IDF/Bag-of-Words is retained but is **diagnostic/descriptive** under the H1/H2
cross-mention transfer boundary; predictable failure under a vocabulary shift is
not the primary H2 comparison. Under ordinary standard LODO it remains a secondary
comparison together with prompt length, token entropy, difficulty, prompt
embeddings, and the other registered baselines. This classification does not alter
H1: H1 is task-state transfer across concept level, while H2 asks whether hidden
states improve on the frozen prompt representation.
