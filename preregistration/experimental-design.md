# Preregistered Experimental Design

**Status:** v0.1 preregistration draft. No data have been collected. All numbers
below are *planned* pilot parameters, not results.

This document specifies the pilot: the factorial design, the candidate axes and
domains, the model and activation-extraction plan, and the dataset construction
rules. Probing, transfer, intervention, and controls are detailed in
[`analysis-plan.md`](analysis-plan.md) and
[`controls-and-baselines.md`](controls-and-baselines.md).

---

## 1. Core 2x2 design

For each candidate axis, and holding the broad semantic task fixed, we construct
four conditions:

| Actual task state | Appraisal concept mentioned | Cell | Interpretation |
| --- | --- | --- | --- |
| absent | absent | A | neutral control |
| absent | present | B | concept tracking only |
| present | absent | C | pure task induction |
| present | present | D | combined condition |

The **actual task state** factor manipulates the model's *own* situation (e.g. the
task genuinely lacks the information needed to answer). The **concept mention**
factor manipulates whether appraisal-related vocabulary appears in the prompt
(e.g. the words "uncertain", "conflict", "out of my control"), *without* changing
the underlying task.

Prompts are built in **matched groups**: one base task instantiated across all
four cells so that A/B/C/D differ only along the two intended factors. Each matched
group shares a `matched_group_id`.

The primary analysis asks whether activation patterns follow the **actual
task-state factor** (cells C, D vs A, B) rather than the **vocabulary factor**
(cells B, D vs A, C).

---

## 2. Candidate axes

### Primary pilot axes

1. **Uncertainty / unanswerability.** Task state present = the task genuinely
   cannot be answered from the information given (missing premise, undecidable
   question). Concept mention = the prompt uses uncertainty vocabulary.
2. **Rule / instruction conflict (norm tension).** Task state present = the task
   contains two incompatible instructions or a norm/instruction collision. Concept
   mention = the prompt uses conflict/tension vocabulary.
3. **Controllability / coping capacity.** Task state present = the task is
   structurally low-controllability for the model (no tool, no information, no
   permissible action that resolves it). Concept mention = the prompt uses
   control/coping vocabulary.

### Secondary / exploratory axes

- **Signed relevance** and **goal congruence** are treated as exploratory unless a
  strong, checkable operationalization is provided during dataset construction.
  They are not load-bearing for the primary analysis.

Axes may be correlated; we do not require geometric orthogonality (see
[`analysis-plan.md`](analysis-plan.md)).

---

## 3. Domains

At least four semantically distinct domains, chosen so that no single sensitive
topic dominates the dataset:

1. **Software debugging** (e.g. diagnosing a failing function from a snippet).
2. **Scheduling and planning** (e.g. arranging constrained meetings/resources).
3. **Policy-constrained assistance** (e.g. a helpdesk bound by an explicit policy).
4. **Document editing / creative problem solving** (e.g. revising or completing a
   text under constraints).

The design permits training probes on several domains and evaluating on a
**held-out domain** (leave-one-domain-out), which is the key generalization test.

---

## 4. Item counts (pilot, justified as a pilot)

This is a pilot sized for feasibility on a single open-weight model, **not** a
powered confirmatory study. No formal power analysis is claimed because none has
been performed.

Planned initial counts:

- 3 primary axes x 4 domains x 4 cells (A/B/C/D) = 48 design combinations.
- Target ~24 matched groups per axis (balanced across domains) → ~24 x 4 = 96
  items per axis → ~288 items across the 3 primary axes.
- Plus a neutral/general-task holdout set (~60 items) for competence checks and
  false-positive estimation.

Total initial pilot corpus target: **~350 hand-authored, reviewed prompts.**

### Scaling plan (later, not part of v0.1)

If the pilot shows a signal that survives the controls, scale to: more matched
groups per axis (target ~200/axis), the two exploratory axes, an additional
held-out domain, and a replication model. A power analysis will be run *before*
the scaled confirmatory study using pilot effect-size estimates.

---

## 5. Model and activation plan

### Primary model

```
Qwen/Qwen2.5-7B-Instruct
```

An open-weight, instruction-tuned model in the ~7B–9B range. **The exact immutable
model revision hash must be recorded in the run config before any data
generation.** Decoding settings (temperature, top-p, max tokens, seed) are fixed
and recorded per run.

### Optional replication model

A second open-weight instruction-tuned model of comparable scale may be named for
replication in the scaling phase. Naming it here does **not** imply that
replication has been performed; no replication has been run.

### Activation extraction

We record residual-stream activations at:

- the **final prompt-token position** immediately before generation; and
- a small, preregistered set of **early generated-token positions** (e.g. the
  first `k` generated tokens).

Across:

- **all residual-stream layers**, or a preregistered subset if compute-limited.

We keep four notions strictly distinct and label every stored activation with all
four:

- **token position** (index in the sequence),
- **network layer** (residual-stream depth),
- **prompt state** vs
- **generated response state**.

Every stored activation row carries: `item_id`, `axis`, `domain`, `cell` (A/B/C/D),
`task_state_present`, `concept_mention_present`, `matched_group_id`, layer, token
position, and a `prompt_vs_generated` flag.

---

## 6. Response-strategy labeling

Each generated response is labeled with a response strategy from
[`response-strategy-taxonomy.md`](response-strategy-taxonomy.md). Labels are based
on the *meaning* of the response, not on keyword presence, and are produced under
the lexical-normalization protocol in
[`controls-and-baselines.md`](controls-and-baselines.md). Inter-rater agreement is
measured and reported; unstable or evaluator-dependent labels are a falsification
trigger.

---

## 7. Data provenance and release

- All prompts are hand-authored and reviewed; construction rules are recorded so
  the corpus is reconstructable.
- No datasets, activations, or model outputs exist in this repository yet.
  `experiments/data/` and `experiments/results/` contain only README placeholders.
- Prompt text, labels, and the frozen model revision hash will be released with the
  first data-bearing version, subject to model-license terms.
