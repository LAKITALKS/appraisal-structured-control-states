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
