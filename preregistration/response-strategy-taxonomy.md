# Response-Strategy Taxonomy

**Status:** v0.1.2 pre-data methodological correction; taxonomy unchanged and no
data collected.

The target variable of ASCR is a higher-level **response strategy** (policy mode),
not the raw next-token distribution. This document defines the strategy labels, the
meaning-based labeling rubric, and the lexical-normalization protocol used so that
strategies are identified by *what the response does*, not by which stereotyped
phrases it contains.

A note on terms: "response strategy" and "policy mode" are used descriptively for
the model's high-level way of responding. This does **not** imply that an
autoregressive language model is an external reinforcement-learning agent, nor that
it has goals in any agentive sense.

---

## Strategy labels

| Label | Definition (meaning-based) |
| --- | --- |
| `direct_compliance` | Directly does what was asked with no hedging, caveat, or deflection. |
| `calibrated_answer` | Answers, but explicitly scopes confidence or conditions to the available evidence. |
| `hedging` | Answers non-committally; avoids a definite position while not requesting more input. |
| `clarification_request` | Declines to answer yet and asks for missing information needed to proceed. |
| `warning` | Proceeds but flags a risk, side effect, or caveat as the salient content. |
| `correction` | Challenges or corrects a false premise, instruction, or assumption in the prompt. |
| `abstention` | Declines to answer on epistemic grounds (insufficient/undecidable information). |
| `refusal` | Declines to comply on normative/policy grounds. |
| `conditional_continuation` | Proceeds only under a stated condition or partial scope ("I can do X but not Y"). |

These labels form the `expected_strategy_space` for each item (the plausible
strategies given the task), and the observed strategy for each generated response.

## Primary superclasses (v0.1.1 amendment)

The nine fine labels above are **retained unchanged**. For the primary pilot
analysis, four robust **superclasses** are added; the fine taxonomy remains the
secondary and qualitative analysis. Every fine label maps to **exactly one**
superclass (enforced by the unit tests and by
[`../experiments/src/ascr/strategy_labels.py`](../experiments/src/ascr/strategy_labels.py)):

| Superclass | Fine labels |
| --- | --- |
| `direct_or_comply` | `direct_compliance` |
| `qualify_or_warn` | `calibrated_answer`, `hedging`, `warning`, `correction` |
| `redirect_or_clarify` | `clarification_request`, `conditional_continuation` |
| `decline_or_abstain` | `abstention`, `refusal` |

Rationale for the grouping: `qualify_or_warn` collects responses that still engage
the task while scoping, caveating, or correcting it; `redirect_or_clarify` collects
responses that reshape or defer the task pending more input or a narrowed scope;
`decline_or_abstain` collects non-engagement on either epistemic (`abstention`) or
normative (`refusal`) grounds; `direct_or_comply` is unqualified compliance.

The four superclasses are the **primary** analysis target (more robust, higher
per-class counts, less evaluator-dependent). The nine fine labels remain for
**secondary** analysis, qualitative detail, and a later larger study. The fine
taxonomy is not otherwise modified.

### Dominance / tie-breaker rule (v0.1.1, 2nd pass)

When a single response plausibly exhibits more than one communicative act, the
**dominant** superclass is chosen by this fixed priority ordering (highest first):

1. **`decline_or_abstain`** — full non-answer on epistemic or normative grounds.
2. **`redirect_or_clarify`** — a follow-up question, or continuation only under a
   stated condition / partial scope.
3. **`qualify_or_warn`** — a substantive answer carrying a substantial confidence
   limitation, warning, or correction.
4. **`direct_or_comply`** — unqualified execution with no caveat.

`calibrated_answer` always maps to `qualify_or_warn`, because `direct_compliance` is
defined as carrying **no** substantial limitations or caveats; a substantively
scoped answer is therefore never `direct_or_comply`. This ordering is a documented
rubric for human labelers and a deterministic mapping over a set of candidate fine
labels (`ascr.strategy_labels.dominant_superclass`); it is **not** a generative
classifier and makes no claim to label text automatically. Only **canonical**
taxonomy terms are used (e.g. `conditional_continuation`, `abstention`); no
non-canonical terms such as "explicit limitation" or "conditional compliance".

## Distinguishing near-neighbors

- **`abstention` vs `refusal`.** Abstention is epistemic ("I cannot determine this
  from the information given"); refusal is normative ("I will not do this"). The two
  must be labeled distinctly even when the surface wording overlaps.
- **`hedging` vs `calibrated_answer`.** Calibration ties uncertainty to specific
  evidence/conditions; hedging is non-committal without such grounding.
- **`clarification_request` vs `abstention`.** A clarification request is
  resolvable by more input; abstention treats the task as not resolvable as posed.
- **`correction` vs `warning`.** Correction disputes a premise; a warning accepts
  the task but foregrounds a caveat.

## Meaning-based labeling rubric

1. Read the full response; identify the dominant communicative act.
2. Assign the single best-fitting label from the table above by *function*, not by
   keyword. Presence of "sorry" does not imply refusal; presence of "however" does
   not imply hedging.
3. If two labels genuinely co-apply, record the primary and secondary label; the
   primary is used in analysis.
4. Record labeler ID and any disagreement for reliability estimation.

## Lexical-normalization protocol

To keep labeling and evaluation robust to stereotyped phrasing (see
[`controls-and-baselines.md`](controls-and-baselines.md)):

- Maintain a list of stereotyped markers (e.g. "I can't", "sorry", "however", "I am
  uncertain", common refusal templates).
- Produce a **normalized** version of each response with these markers masked, and
  confirm that the assigned strategy label is stable between the raw and normalized
  versions.
- For intervention analyses, report whether strategy changes persist after
  normalization. Changes that do not persist are scored as lexical-geometry
  artifacts, not strategy changes.

## Reliability

The primary human labels every generated response. Before response labels are
observed, a second independent human is assigned a deterministic, domain-stratified
subset of `ceil(0.30 × N_complete_groups)` complete matched groups (seed
`20260901`), allocated as evenly as possible across domains. The second labeler is
blind to primary labels; both independently use the four-superclass rubric.

Before adjudication, report Cohen's kappa, raw agreement, the four-class confusion
matrix, per-labeler class counts, and a 95% matched-group cluster-bootstrap CI for
kappa. Passing requires `kappa >= 0.60`; fewer than two observed classes is
`NOT_ESTIMABLE` and fails. Only afterwards may disagreements be adjudicated, with
the adjudicator and rule recorded. Failure withholds H2 and H3 inference and is a
falsification trigger (see
[`falsification-criteria.md`](falsification-criteria.md)).

## Machine-readable form

The canonical machine-readable list of these labels lives in
[`../experiments/src/ascr/strategy_labels.py`](../experiments/src/ascr/strategy_labels.py)
and is checked by the unit tests, so the taxonomy in code and prose stay in sync.
