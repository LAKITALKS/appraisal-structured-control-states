# Novelty Statement

## Verdict

**Novel combination.**

This is not claimed to be an unprecedented discovery, and it is not presented as
an unqualified "strong novelty candidate". The individual components of the
Appraisal-Structured Latent Control Representations (ASCR) hypothesis are, to
varying degrees, already present in prior work. The contribution is a unifying,
falsifiable synthesis and a methodological dissociation that, to our knowledge,
has not been jointly tested.

## What is already established by prior work

Existing, verified work provides evidence for the components separately:

- Causally efficacious latent directions and steering
  [`zou2023repe`; `turner2023actadd`; `mack2024melbo`].
- A refusal direction, and evidence that refusal involves more than one direction
  [`arditi2024refusal`; `joad2026morerefusal`].
- Conditional, rule-triggered behavioral steering [`lee2024cast`].
- Uncertainty representations and (un)answerability directions
  [`teplica2025sciurus`; `lavi2025unanswerability`].
- Evaluation-awareness states and their manipulation
  [`nguyen2025evalaware`; `hua2025evaldeployed`].
- Internal-activation safety signals separating recognition from action
  [`han2025safeswitch`].
- Task representations that form on the fly and transfer [`li2025taskrepr`].
- Emotion-concept vectors, appraisal variables during emotion inference, and
  valence/arousal geometry
  [`tak2025emotioninfer`; `sofroniew2026emotion`; `sun2026valencearousal`].
- Hidden-state (un)answerability and abstention decomposed into distinct axes
  [`slobodkin2023unanswerability`; `wagner2026twoaxes`].
- Task-induced norm/role representations that are separately steerable
  [`wang2026privacy`; `zeng2025roleconflict`].
- Task-induced difficulty as a linear, decodable property
  [`lee2025difficulty`].
- Functional dissociation of uncertainty from correctness features
  [`patel2026uncertaintycorrectness`].
- Multi-attribute steering with per-attribute orthogonality constraints
  [`nguyen2025matsteer`].

### Boundary tightened in the v0.1.1 amendment

The newly verified prior art (2026-07-12) narrows the novelty of the **individual
axes** considerably: uncertainty/answerability, norm/role tension, and difficulty
are each already decodable and, in several cases, steerable task-induced states.
This makes explicit a distinction that must be defended, not assumed:

> Demonstrating several individual task-state directions — even three — is **not**
> the same as demonstrating a shared, appraisal-structured control *family*. Three
> already-known directions spanning a 3-D subspace are not a family.

The defensible novelty therefore rests on the **shared structure**, tested by the
preregistered family-structure test (amendment §5): a shared low-rank model must
beat equally complex separate directions on held-out domains, show structured
behavioral specificity, and add incremental response-strategy variance beyond known
single directions and simple baselines (including a difficulty-representation
baseline). Multi-attribute steering [`nguyen2025matsteer`] is the closest prior
method, but it enforces near-orthogonality across externally-labeled attributes and
does not test a shared task-induced control family; ASCR's identifiability
(not-orthogonality) framing and family-structure test are the distinguishing
contribution.

## What ASCR proposes

The unifying hypothesis is that several of these findings may be **special cases
or partial projections** of a more general family of *task-induced,
appraisal-structured latent control representations* of the model's own current
task situation, which partially govern **response-strategy selection** across
semantic domains.

The central methodological distinction is between:

- **Semantic concept tracking** — the prompt names or describes an
  appraisal-related concept (uncertainty, conflict, control), while the model's
  own task remains straightforward; and
- **Task-induced, system-relative state** — the model's *actual current task*
  contains ambiguity, incompatible constraints, low controllability, unresolved
  goal tension, or response pressure, even when the prompt does not name those
  concepts.

## Calibrated language used throughout

- "To our knowledge, we found no prior work that *jointly* tests the full
  conjunction."
- "Existing work establishes the components separately."
- "The proposed contribution is a unifying, falsifiable synthesis."

We deliberately avoid "no one has ever" and any claim of a demonstrated mechanism.
Nothing in this repository reports experimental results; it is a preregistered
hypothesis and design.

## What is explicitly *not* claimed

ASCR does not claim to establish subjective experience, feeling, consciousness,
sentience, suffering, phenomenal states, biological equivalence, a contemplative
or Buddhist mechanism inside a Transformer, a universal architecture shared by all
language models, or the final correct number of latent dimensions. See the
Limitations and Non-Claims section of the paper and
[`../preregistration/falsification-criteria.md`](../preregistration/falsification-criteria.md).
