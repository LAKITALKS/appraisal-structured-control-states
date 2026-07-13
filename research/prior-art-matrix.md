# Prior-Art Matrix

This document maps the closest prior work to the individual components of the
Appraisal-Structured Latent Control Representations (ASCR) hypothesis, and marks
which parts of the proposed **conjunction** each work already covers. Every cited
work is verified against a primary source (see
[`citation-verification.md`](citation-verification.md)).

The purpose is to make the novelty claim honest and checkable: the components are
mostly present in prior work; the proposed contribution is their unifying,
falsifiable synthesis, and specifically the dissociation of *task-induced
system-relative state* from *semantic concept tracking*.

## Component columns

- **C1 — Causal latent direction.** Work identifies a latent direction/subspace
  and shows a causal effect on behavior via steering or ablation.
- **C2 — Strategic behavior target.** The controlled behavior is a response
  strategy (refuse, abstain, report uncertainty, correct) rather than only topic
  or sentiment.
- **C3 — Task-induced (not concept-tracking).** The representation reflects the
  model's *own current task situation* rather than an appraisal-related concept
  named in the prompt.
- **C4 — Cross-domain transfer.** Evidence that the representation generalizes
  across semantically disjoint task domains.
- **C5 — Multi-axis / integrated appraisal structure.** Work considers several
  distinct control variables (e.g. uncertainty, controllability, norm tension)
  rather than a single axis.
- **C6 — Lexical-geometry control.** Work explicitly rules out the deflationary
  account that a direction only reweights stereotyped output phrases.

Legend: ● covered · ◐ partial / related · ○ not addressed.

| Work | C1 | C2 | C3 | C4 | C5 | C6 |
| --- | :-: | :-: | :-: | :-: | :-: | :-: |
| Zou et al. 2023, Representation Engineering [`zou2023repe`] | ● | ◐ | ◐ | ◐ | ◐ | ○ |
| Turner et al. 2023, Activation Engineering (ActAdd) [`turner2023actadd`] | ● | ○ | ○ | ◐ | ○ | ◐ |
| Arditi et al. 2024, Single refusal direction [`arditi2024refusal`] | ● | ● | ◐ | ◐ | ○ | ◐ |
| Joad et al. 2026, More than a single direction [`joad2026morerefusal`] | ● | ● | ◐ | ◐ | ◐ | ◐ |
| Lee et al. 2024, Conditional Activation Steering [`lee2024cast`] | ● | ● | ◐ | ○ | ◐ | ○ |
| Teplica et al. 2025, SCIURus (uncertainty) [`teplica2025sciurus`] | ● | ◐ | ◐ | ◐ | ○ | ○ |
| Lavi et al. 2025, (Un)answerability directions [`lavi2025unanswerability`] | ● | ● | ● | ◐ | ○ | ○ |
| Nguyen et al. 2025, Evaluation awareness [`nguyen2025evalaware`] | ● | ◐ | ● | ◐ | ○ | ○ |
| Hua et al. 2025, Steering eval-aware to "deployed" [`hua2025evaldeployed`] | ● | ◐ | ● | ○ | ○ | ○ |
| Han et al. 2025, SafeSwitch [`han2025safeswitch`] | ● | ● | ● | ◐ | ◐ | ○ |
| Li et al. 2025, Just-in-time task representations [`li2025taskrepr`] | ◐ | ○ | ● | ● | ○ | ○ |
| Tak et al. 2025, Emotion inference / appraisal [`tak2025emotioninfer`] | ● | ○ | ○ | ◐ | ● | ○ |
| Sofroniew et al. 2026, Emotion concepts & function [`sofroniew2026emotion`] | ● | ◐ | ◐ | ● | ◐ | ○ |
| Sun et al. 2026, Valence-arousal subspace [`sun2026valencearousal`] | ● | ● | ◐ | ◐ | ◐ | ○ |
| Mack & Turner 2024, MELBO (unsupervised) [`mack2024melbo`] | ● | ◐ | ◐ | ◐ | ◐ | ○ |
| Slobodkin et al. 2023, Hidden-state (un)answerability [`slobodkin2023unanswerability`] | ◐ | ● | ● | ◐ | ○ | ○ |
| Wagner 2026, Two axes of abstention [`wagner2026twoaxes`] | ◐ | ● | ● | ◐ | ◐ | ○ |
| Wang et al. 2026, Contextual privacy norms [`wang2026privacy`] | ● | ◐ | ● | ◐ | ◐ | ○ |
| Zeng 2025, Role conflicts in instruction following [`zeng2025roleconflict`] | ● | ◐ | ● | ○ | ○ | ○ |
| Lee et al. 2025, Difficulty perception [`lee2025difficulty`] | ◐ | ○ | ● | ◐ | ○ | ○ |
| Patel et al. 2026, Uncertainty vs correctness (SAE) [`patel2026uncertaintycorrectness`] | ● | ◐ | ● | ◐ | ◐ | ○ |
| Nguyen et al. 2025, Multi-attribute steering (MAT-Steer) [`nguyen2025matsteer`] | ● | ◐ | ○ | ◐ | ● | ○ |
| **ASCR (this repository, proposed)** | ● | ● | ● | ● | ● | ● |

## Reading of the matrix

- **C1 (causal direction)** is well covered. That latent directions can causally
  move behavior is not in dispute and is not claimed as novel here.
- **C2 (strategic target)** is covered for refusal, abstention, and unanswerability
  in particular.
- **C3 (task-induced state)** is the most important distinction. A subset of work
  already probes state that is endogenous to the model's own situation — most
  clearly unanswerability [`lavi2025unanswerability`], evaluation awareness
  [`nguyen2025evalaware`; `hua2025evaldeployed`], and internal safety signals
  [`han2025safeswitch`]. Much emotion/appraisal work instead tracks *concepts*
  named or described in the prompt [`tak2025emotioninfer`;
  `sofroniew2026emotion`], which is exactly the confound ASCR is designed to
  separate.
- **C4 (cross-domain transfer)** is partially covered; task-representation work
  [`li2025taskrepr`] and emotion-concept generalization [`sofroniew2026emotion`]
  are the closest.
- **C5 (multi-axis appraisal structure)** appears mostly in the emotion/affect
  literature [`tak2025emotioninfer`; `sun2026valencearousal`], which uses appraisal
  variables or valence/arousal geometry, but for *third-person* emotion inference
  or affective text generation rather than the model's own response-strategy
  selection.
- **C6 (lexical-geometry control)** is essentially absent as an explicit, primary
  control in the works surveyed. This is a methodological gap ASCR treats as
  mandatory.

## The gap ASCR targets

No single verified work in this matrix jointly delivers all of: (a) a
task-*induced*, system-relative state, dissociated from concept tracking by
design; (b) an *integrated multi-axis* appraisal structure governing response
strategy; (c) *cross-domain* transfer of that structure; and (d) a *mandatory
lexical-geometry control* separating strategy change from stereotyped-phrase
reweighting. ASCR's contribution is this conjunction as a preregistered,
falsifiable hypothesis — not the discovery of any one component.

## Amendment v0.1.1 additions (verified 2026-07-12)

These seven works were added in the v0.1.1 pre-data amendment after an independent
prior-art review. Each is verified against its primary source (see
[`citation-verification.md`](citation-verification.md)). They tighten the boundary
around the **individual** ASCR axes; none tests the **shared control family**,
which is precisely what the new family-structure test (amendment §5) targets.

### `slobodkin2023unanswerability` — The Curious Case of Hallucinatory (Un)answerability
- **Method:** probes hidden states for query answerability; the first decoded
  token's representation is a strong answerability indicator; improved decoding.
- **Overlap with ASCR:** direct overlap on the *uncertainty/unanswerability* axis as
  a task-induced, hidden-state property.
- **Already covered:** that (un)answerability is internally represented and
  task-induced.
- **ASCR must additionally test:** cross-domain transfer of this axis *and* whether
  it is part of a shared control family alongside norm tension and controllability,
  with the lexical-geometry control.
- **Category:** methodological precursor / partial overlap (single axis).

### `wagner2026twoaxes` — Two Axes of LLM Abstention
- **Method:** dual-threshold calibrated policy separating answer correctness from
  question answerability using confidence scores and hidden-state probes.
- **Overlap with ASCR:** two task-induced axes (answerability, correctness) driving
  an abstention/refusal decision.
- **Already covered:** that abstention decomposes into at least two distinct
  internal axes.
- **ASCR must additionally test:** whether these axes join controllability and norm
  tension in a shared appraisal-structured family, and whether steering (not just a
  threshold policy) moves response strategy specifically.
- **Category:** partial overlap (multi-axis within one behavior).

### `wang2026privacy` — Do LLMs Know What Is Private Internally?
- **Method:** probing and steering of contextual-integrity parameters (information
  type, recipient, transmission principle); CI-parametric steering intervenes along
  each dimension independently.
- **Overlap with ASCR:** a task-induced, multi-parameter *norm* representation that
  is separately steerable — close to the norm-tension axis and to the
  identifiability framing.
- **Already covered:** that norm-relevant contextual parameters are separately
  decodable and steerable.
- **ASCR must additionally test:** whether norm tension shares structure with
  uncertainty and controllability, and whether the effect survives lexical
  normalization and predicts response strategy rather than a privacy label.
- **Category:** partial overlap / potential novelty threat to the norm-tension axis.

### `zeng2025roleconflict` — Who is In Charge? Dissecting Role Conflicts
- **Method:** linear probing and Direct Logit Attribution of system-vs-user
  instruction conflicts, with steering of "social-cue" vectors.
- **Overlap with ASCR:** task-induced *instruction/role conflict* is close to the
  norm-tension axis.
- **Already covered:** that instruction conflict is linearly encoded and causally
  steerable.
- **ASCR must additionally test:** cross-domain generality, shared-family
  membership, and strategy-level (not token-logit) effects under the QA protocol.
- **Category:** partial overlap (single axis, norm tension).

### `lee2025difficulty` — Probing the Difficulty Perception Mechanism
- **Method:** linear probe on final-token representations recovers math-problem
  difficulty; specific final-layer heads show opposite patterns for easy/hard;
  difficulty is high-dimensional linear.
- **Overlap with ASCR:** *generic difficulty* is a strong confound for the
  task-state axes and must be controlled, not conflated with appraisal structure.
- **Already covered:** that difficulty is linearly decodable and task-induced.
- **ASCR must additionally test:** that task-state axes add value **beyond** a
  difficulty representation (new primary baseline, amendment §11).
- **Category:** competing explanation / mandatory baseline.

### `patel2026uncertaintycorrectness` — Uncertainty vs Correctness (SAE dissociation)
- **Method:** sparse autoencoders partition features into pure-uncertainty,
  pure-incorrectness, and confounded populations; suppression shows distinct causal
  roles.
- **Overlap with ASCR:** directly relevant to the uncertainty axis and to the
  identifiability/selective-manipulability framing.
- **Already covered:** that uncertainty and correctness are functionally
  dissociable, causally distinct feature sets.
- **ASCR must additionally test:** whether uncertainty is one member of a shared
  control family and whether difference-in-means steering (not SAE feature
  suppression) modulates response strategy specifically.
- **Category:** partial overlap / complementary method.

### `nguyen2025matsteer` — Multi-Attribute Steering (MAT-Steer)
- **Method:** learns per-attribute steering vectors with sparsity and orthogonality
  constraints to reduce inter-attribute conflict (ACL 2025).
- **Overlap with ASCR:** the multi-axis, selectively-manipulable steering framing;
  the closest prior work on *jointly* steering several attributes.
- **Already covered:** that multiple attribute directions can be learned and steered
  with reduced interference.
- **ASCR must additionally test:** that its axes are *task-induced situation*
  representations (not externally-labeled attributes like toxicity/bias), and that a
  **shared low-rank** family beats equally complex separate directions on held-out
  domains — MAT-Steer enforces near-orthogonality across attributes and does not
  test a shared family.
- **Category:** complementary research / methodological reference (contrasts with the
  identifiability-not-orthogonality framing).
