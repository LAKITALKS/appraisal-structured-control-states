# ASCR v0.1.1 Pre-Data Amendment

**Amendment date:** 2026-07-12
**Applies to:** the v0.1.0 preregistration (archived; Zenodo version DOI
[10.5281/zenodo.21294933](https://doi.org/10.5281/zenodo.21294933), concept DOI
[10.5281/zenodo.21294932](https://doi.org/10.5281/zenodo.21294932)).
**Author:** Lazaros Varvatis, Independent Researcher, Berlin, Germany.

---

## 1. Status

- **No data have been collected.** No model has been run, no activations have been
  extracted, and no results exist. This amendment was written strictly **before
  the first data collection**.
- The archived **v0.1.0 preregistration remains unchanged**. This amendment does
  not overwrite, retract, or silently rewrite it; it *adds* precommitments and
  documents each one below and in [`../CHANGELOG.md`](../CHANGELOG.md).
- **The original hypotheses are not altered in light of any result**, because there
  is no result. The changes below tighten operationalizations and add controls; the
  substantive hypotheses H1–H4 are preserved (see §4).

### Precisified points (summary; details in §5–§11)

1. An explicit, preregistered **family-structure test** for the shared-control
   claim (§5).
2. A single, preregistered **primary direction-derivation** rule (§6).
3. A binding **concept-mention (cell B/D) stimulus-QA protocol** (§7).
4. A two-tier **response-strategy taxonomy** with four primary superclasses (§8).
5. A modular, versioned **mini-shard** pilot protocol with immutable run manifests
   (§9).
6. A constraint that the **replication model must differ from the primary model**
   (§10).
7. An expanded, primary-source-**verified prior-art** set and matching baselines
   (§11).

---

## 2. Reason for the amendment

An independent methodological and prior-art review — conducted before any data
collection — identified a specific gap in the v0.1.0 design:

- **Gap between single axes and the family claim.** H1–H3 can each succeed while
  the model merely contains three *independent, already-known-or-partially-known*
  directions (task-induced uncertainty/unanswerability, norm tension, low
  controllability). Demonstrating three decodable directions does **not** by itself
  establish a shared, *appraisal-structured control family*. The stronger family
  claim therefore needs its own operationalized, falsifiable test.
- **Tighter prior-art boundary.** Newly verified prior art narrows the novelty of
  the individual axes further: abstention along correctness-vs-answerability axes
  [`wagner2026twoaxes`], contextual privacy/norm representations
  [`wang2026privacy`], role-conflict resolution [`zeng2025roleconflict`],
  hidden-state (un)answerability [`slobodkin2023unanswerability`], difficulty
  perception [`lee2025difficulty`], a functional dissociation of uncertainty vs
  correctness via sparse autoencoders [`patel2026uncertaintycorrectness`], and
  multi-attribute steering with orthogonality constraints
  [`nguyen2025matsteer`]. Several of these are close to individual ASCR axes; the
  defensible contribution is the *shared structure*, not any single axis.
- **Primary new safeguard.** The central new safeguard is an explicit test of the
  *shared structure* (§5), plus a precommitted direction-derivation rule (§6) and a
  stimulus-quality protocol (§7) that removes confounds which could otherwise
  inflate H1.

This is a **precommitment**, not a post-hoc discovery. Nothing here is presented as
a result.

---

## 3. Scientific framing (unchanged core)

The distinction between **task induction** (the model's own task actually contains
the property) and **semantic concept tracking** (the prompt merely names or
describes the property) remains the core idea, and the family claim remains a
*novel combination* rather than a demonstrated mechanism. The key sharpening is:

> Demonstrating several individual task-state directions is **not** evidence of a
> shared ASCR control family. v0.1.1 defines, before data collection, what
> additional evidence is required for the family claim.

---

## 4. Unchanged components

The following remain exactly as in v0.1.0 and are **not** modified by this
amendment:

- the central **task-state vs concept-mention** distinction;
- the **2×2 design** (actual task state × concept mention);
- **H1** — task-state dissociation;
- **H2** — cross-domain and incremental structure;
- **H3** — causal response-strategy modulation (sufficiency and necessity);
- **H4** — ordered emergence, retained as an **exploratory** hypothesis;
- the **three primary pilot axes** (uncertainty/unanswerability, norm tension,
  controllability/coping);
- the **four pilot domains** (software debugging, scheduling/planning,
  policy-constrained assistance, document editing);
- the **non-claims** (no subjective experience, feeling, consciousness, sentience,
  suffering, phenomenal states, biological equivalence, no universal architecture,
  no final dimension count);
- the mandatory **lexical-geometry** and **competence** controls.

Explicitly **out of scope** for v0.1.1 (not added): any holonomy hypothesis, any
"H5", and any latent-error-model (LEM) extension.

---

## 5. New precisification: family-structure test

The family claim is **not** derived from the existence of three decodable
directions. A three-dimensional subspace spanned by three axis directions is *not*
a family. The shared-control claim is preregistered with a three-part test whose
components are **all required**: **family claim = A ∧ B ∧ C**. No single advantage
from any list suffices. Full statistical detail — rank grid, primary log-loss
metric, and paired-bootstrap decision rules — is in
[`analysis-plan.md`](analysis-plan.md) §6b "Family-structure test".

**A. Shared low-rank model vs separate models.** A shared bottleneck `Q` (rank `r`)
with axis-specific logistic heads, trained multi-task, versus separate regularized
per-axis logistic models, on identical matched-group splits with leave-one-domain-out
transfer and strictly nested cross-validation. Rank grid is `r ∈ {1, 2}` for three
axes (`r = 3` secondary sensitivity only; `r = 1` admissible for two axes). Primary
metric: pooled held-out log-loss. **Decision:** the paired matched-group bootstrap of
`log_loss_shared − log_loss_separate` must lie entirely below zero after FDR; no
arbitrary margin is used. Secondary metrics are reported but do not decide.

**B. Structured behavioral specificity.** An intervention-effect matrix
`E[axis, response_superclass]` with a preregistered per-axis target strategy set,
stated in canonical taxonomy terms only. **Decision:** the bootstrap CI of the
per-axis selectivity contrast (mean effect on target strategies minus mean absolute
effect off-target) must be above zero, the effect must not reduce to generic
refusal/negativity/fluency degradation, competence controls must pass, and the effect
must persist after lexical normalization.

**C. Incremental shared contribution.** Nested comparison of
`known single directions + simple baselines` vs
`known single directions + simple baselines + shared ASCR representation`, primary
metric held-out response-strategy log-loss. **Decision:** the paired bootstrap CI of
the improvement must lie entirely above zero after FDR.

This test is a **preregistered addition**, not a post-hoc discovery. All three
components are required; failing any one leaves the family claim unsupported.

---

## 6. New precisification: primary direction derivation

To remove analytic degrees of freedom, one **primary** steering direction is fixed
in advance (full rule in
[`controls-and-baselines.md`](controls-and-baselines.md) §"Primary direction
derivation"):

1. **Primary decoding:** regularized logistic regression.
2. **Primary intervention direction:** the normalized **difference-in-means** of
   activations between task-state-present and task-state-absent, computed **only**
   from training groups, with the concept-mention factor **balanced** within the
   training data.
3. Probe weights, LDA, and ridge directions are **declared robustness analyses**
   only.
4. **Layer selection** uses training/validation data only; the test set is never
   used to pick layer or direction.
5. **Intervention strengths** are fixed in advance; the best strength is never
   chosen on the final test set.
6. Directions and controls share **identical norm**.
7. Controls: matched-norm random directions, PCA directions, and known
   unanswerability/refusal/difficulty directions where reproducible.

Where this differs from the more permissive v0.1.0 phrasing ("logistic regression,
ridge, LDA as candidates"), the change is documented here and in the CHANGELOG; the
difference-in-means intervention direction is now the single primary rule.

---

## 7. New precisification: concept-mention (B/D) quality protocol

A binding stimulus-QA protocol governs the concept-mention cells so that cell B is
not more artificial or metalinguistic than cell A, and concept mention does not
covary with difficulty. Full protocol in
[`experimental-design.md`](experimental-design.md) §"Concept-mention stimulus-QA
protocol". Minimum checks: naturalness, grammatical plausibility, register, prompt
length, syntactic complexity, domain identity, target task, solvability, the true
presence/absence of the task state, the concept mention, avoidance of direct label
leaks, and avoidance of artificial meta-sentences. Bad matched groups are revised
or discarded **before** any activation is extracted.

---

## 8. New precisification: two-tier response-strategy taxonomy

The nine fine-grained labels are retained unchanged. Four **primary superclasses**
are added for the primary pilot analysis, with a fixed, tested one-to-one mapping
from each fine label to exactly one superclass:

- `direct_or_comply`
- `qualify_or_warn`
- `redirect_or_clarify`
- `decline_or_abstain`

The fine taxonomy remains the **secondary** and qualitative analysis. See
[`response-strategy-taxonomy.md`](response-strategy-taxonomy.md); the mapping is
enforced by unit tests.

---

## 9. New precisification: modular mini-shards

The pilot is executable as versioned **mini-shards**, each testing a single axis,
without pretending to be the full confirmatory study:

- **ASCR-Mini-0** — uncertainty/unanswerability; pipeline/stimulus/H1 feasibility;
  a few preregistered layers; final prompt-token readout; no full steering sweep.
- **ASCR-Mini-1** — norm tension.
- **ASCR-Mini-2** — controllability.

Each shard carries an **immutable run manifest** (experiment ID, shard ID,
prompt-set version, model name, immutable model revision, tokenizer revision, chat
template, code commit, seed, decoding config, layer, token position, stimulus-file
hash, environment, timestamp). Shards may be combined only if all
compatibility-relevant fields are identical. No cherry-picking or merging of only
positive shards. Details in [`experimental-design.md`](experimental-design.md)
§"Modular mini-shard protocol".

---

## 10. New precisification: models and replication

- **Primary model:** `Qwen/Qwen2.5-7B-Instruct` (unchanged). The exact immutable
  revision hash must be recorded before the first data collection.
- **Replication model:** must **not** be `Qwen/Qwen2.5-7B-Instruct` again. Until a
  documented, compatibility-checked choice is made, the config holds the placeholder
  `TO_BE_SELECTED_BEFORE_CONFIRMATORY_REPLICATION`.
- The mini-pilot may initially test only one axis. The full family claim (§5) may be
  assessed only once at least two, ideally three, axes are adequately
  operationalized and tested.

---

## 11. New precisification: prior art and baselines

Seven primary-source-verified works are added and categorized in
[`../research/prior-art-matrix.md`](../research/prior-art-matrix.md) and
[`../research/citation-verification.md`](../research/citation-verification.md), and
the novelty boundary is tightened in
[`../research/novelty-statement.md`](../research/novelty-statement.md). The baseline
battery is updated so that a **prompt-embedding** baseline and a **difficulty
representation** baseline are explicit primary comparisons; see
[`controls-and-baselines.md`](controls-and-baselines.md) §"Baseline battery
(v0.1.1)".

---

## 12. No-data declaration

No datasets, activations, model outputs, probe results, steering results, figures,
or statistics exist in this repository or are produced by this amendment. Every
number in the design is a *planned* parameter. This amendment only tightens the
preregistration prior to data collection.
