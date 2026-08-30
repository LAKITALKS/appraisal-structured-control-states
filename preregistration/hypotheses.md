# Preregistered Hypotheses

**Project:** Toward Appraisal-Structured Latent Control Representations in Language
Models (ASCR)
**Status:** v0.1 hypotheses; H1's decision statistic is corrected by the v0.1.2
pre-data methodological correction; no data collected.
**Author:** Lazaros Varvatis, Independent Researcher, Berlin, Germany.

This document states the hypotheses that the pilot is designed to test. Each is
written to be independently falsifiable. Falsification criteria are collected in
[`falsification-criteria.md`](falsification-criteria.md); the analysis that maps
each hypothesis to a decision rule is in [`analysis-plan.md`](analysis-plan.md).

---

## Framing and definitions

Let `H_t` denote the residual-stream activation state of an open-weight,
instruction-tuned language model at token position `t` and a chosen layer. We
hypothesize the existence of a small family of low-dimensional, potentially
correlated **control coordinates** `Z_t` that can be extracted from `H_t`:

```
Z_t = Pi_A(H_t),   dim(Z_t) << dim(H_t)
```

`Z_t` is treated as a *candidate* object, not a proven natural kind. We do not
assume a single universal projection `Pi_A` shared across models or layers, and we
do not assume a fixed six-dimensional vector. Candidate control axes include:
signed relevance, uncertainty, goal congruence, controllability/coping capacity,
rule/norm tension, and response pressure/action tendency. We treat **goal
congruence** and **controllability/coping** as priority hypotheses among these,
not as established axes.

The **target variable** is a higher-level *response strategy* (policy mode), not
the raw next-token distribution. See
[`response-strategy-taxonomy.md`](response-strategy-taxonomy.md).

The core empirical distinction is between:

- **Concept tracking:** the prompt *names or describes* an appraisal-related
  concept while the model's own task is straightforward.
- **Task induction:** the model's *own current task* contains the property
  (ambiguity, incompatible constraints, low controllability, goal tension,
  response pressure), whether or not the prompt names it.

---

## H1 — Task-state dissociation

**Statement.** Actual task-induced uncertainty, constraint conflict, or low
controllability is decodable from model activations independently of the presence
of appraisal-related vocabulary. A probe trained to recover the *actual task
condition* tracks that condition more strongly than it tracks lexical concept
mentions.

**Prediction.** In the 2x2 design (task-state present/absent x concept mentioned
present/absent), a task-state probe transfers from concept-absent cells A/C to
concept-present cells B/D and in the reverse direction, while also transferring to
an unseen semantic domain. The pooled out-of-fold balanced-accuracy interval is
evaluated under the v0.1.2 decision rule.

**Primary. Weakened if** the upper 95% cluster-bootstrap interval of the pooled
double-crossed LODO balanced accuracy is at or below 0.5 after technical and QA
gates pass. An interval overlapping 0.5 is indeterminate. The historical B/C
probe-accuracy difference is non-identifying and non-deciding.

---

## H2 — Cross-domain and incremental structure

**Statement.** Task-induced control representations transfer across semantically
disjoint domains and predict response strategy *beyond* a battery of simpler
baselines: lexical features, prompt length, surface sentiment, valence/arousal
baselines, generic task difficulty, confidence or unanswerability alone, and a
single refusal direction.

**Prediction.** A probe trained on a subset of domains and evaluated on a
held-out domain retains predictive value for response strategy above chance and
above the strongest simple baseline, and adds incremental predictive value in a
nested model comparison that already includes those baselines.

**Primary. Falsified if** cross-domain transfer collapses to chance, or if simpler
baselines match the task-state representation with no incremental value.

---

## H3 — Causal response-strategy modulation

**Statement.** Intervening along an identified task-state direction shifts the
model's response strategy in the predicted direction, while preserving general
linguistic competence as far as possible. Both sufficiency and necessity are
tested.

**Prediction.**
- *Sufficiency:* matched-norm activation addition (steering) along the identified
  direction increases the rate of the predicted strategy relative to matched-norm
  random-direction and PCA-direction controls.
- *Necessity:* directional ablation / projection removal / counter-steering
  reduces the predicted strategy relative to the same controls.
- The effect is *strategy-specific* and dose-dependent where predicted, and does
  not reduce to degraded fluency or a generic increase in refusal.

**Primary. Falsified if** steering effects are indistinguishable from matched
random controls, ablation has no specific behavioral effect, or interventions only
degrade competence or produce generic refusal.

---

## H4 — Ordered emergence (secondary)

**Statement.** Coarse signed-relevance or task-pressure signals may become
decodable earlier (earlier layers / earlier token positions) than integrated
task-appraisal structure, while explicit response-strategy commitment may appear
later or closer to output generation.

**Prediction.** Layer- and position-resolved probes show earlier reliable
decoding of coarse pressure/relevance signals than of the integrated multi-axis
structure, and latest reliable decoding for committed strategy.

**Secondary.** This is labeled secondary because the current literature does not
justify a strong confirmatory ordering claim. It is exploratory and will be
reported as such regardless of outcome.

---

## Relationship between hypotheses

H1 establishes that the object of study is task-induced state rather than
vocabulary. H2 establishes that the object is general (transfers) and non-redundant
(incremental). H3 establishes that it is causal and specific. H4 is an exploratory
probe of temporal/depth structure. H1–H3 are the load-bearing claims; the central
interpretation stands or falls with them.
