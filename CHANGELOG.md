# Changelog

All notable changes to this repository are documented here. This project follows
[Semantic Versioning](https://semver.org/) for its metadata version field.

## [0.1.2] — Unreleased (pre-data methodological correction)

This review-branch correction was prepared before any data collection. It does not
alter the archived v0.1.0 or v0.1.1 versions and is not yet merged, tagged,
released, or archived.

### Added

- `preregistration/amendment-v0.1.2.md`, formally documenting why the historical
  B/C H1 accuracy-difference statistic is non-identifying and defining its
  replacement.
- A double-crossed H1 split planner: both concept-mention transfer directions
  within all four outer LODO folds, with whole matched groups confined to one side.
- Nested matched-group selection plans that expose only outer-training domains to
  layer and logistic-regularization selection.
- Pure Layer-0 user-content mask/pooling and final-non-padding-index utilities.
- Explicit `technical_smoke` versus `scientific_feasibility` manifest types and
  structural incompatibility rules.
- A v0.1.2 Mini-0 run-plan template containing blocking pre-data sentinels.
- A deterministic paper-build setting tied to the amendment date, preventing
  review PDFs from differing only in generated timestamp metadata.
- Tests for the corrected H1 design, leakage boundary, tokenizer masks, axis QA,
  smoke separation, historical readability, metadata, and no-data guards.
- **Second correction pass (post-audit).** A frozen, machine-enforced statistical
  specification: the H2 target and fixed four-superclass vocabulary, the paired
  estimand `delta_H2 = log_loss_prompt_embedding - log_loss_hidden_state` with its
  sign convention and positive/weakened/indeterminate rules, the conservative
  `NOT_ESTIMABLE` and unseen-class handling with a fixed float64 log-loss clipping
  rule, the `StandardScaler` + L2 `lbfgs` logistic pipeline, the frozen grid
  `C ∈ {1e-4 … 100}`, the inner selection objectives and tie-breaks with one
  numerical tolerance, and the frozen seed roles (primary `0`; sensitivity
  `1–4`; bootstrap `20260830`; permutation `20260831`).
- Inner **leave-one-training-domain-out** selection folds replacing the earlier
  round-robin mixed-domain inner folds (`ascr.splits.plan_inner_selection_folds`,
  `InnerSelectionFold.inner_validation_domain`).
- A design-time domain-stratified matched-group cluster-bootstrap planner
  (`ascr.splits.plan_cluster_bootstrap`) that returns drawn group identifiers only.
- An operational Benjamini–Hochberg procedure at `q = 0.05` over preregistered
  one-sided raw p-values: a matched-group task-state-label-swap randomization test
  for the H1 secondary family and a paired model-block exchange permutation test
  for the H2 secondary family, both with 10,000 permutations, the `+1` correction,
  and the frozen permutation seed.
- The integrated pre-run gate `ascr.schema.integrated_pre_run_gate_problems`, which
  the future runner must clear before constructing or loading any model.
- **Final pre-release review.** The authoritative gate now requires four mutually
  compatible artifacts — config, frozen Mini-0 run plan, immutable manifest, and
  canonical typed stimulus payload — and a config-only helper is permanently
  fail-closed. Model/tokenizer/embedding/code revisions require full 40-hex commits;
  stimulus and chat-template identities require `sha256:<64 hex>` digests.
- Mini-0 stimulus gates enforce the uncertainty axis, all four registered domains,
  at least 40 complete run-ready groups, and domain counts with `max - min <= 1`;
  split and bootstrap planners reject mixed axes or missing domains.
- A deterministic, pre-label second-reviewer subset planner implementing
  `ceil(0.30 × N_groups)`, domain stratification, and seed `20260901`.
- One canonical release build: `make paper` / `make paper-release` use Tectonic
  0.16.9 in deterministic mode with no engine fallback; `make paper-verify` builds
  twice from clean and requires identical SHA-256; `make paper-dev` is an
  explicitly noncanonical `latexmk` development build.
- Regression suites that fail if
  any of the above is altered, if a document mislabels a raw interval as already
  BH-adjusted, if the canonical build could switch engines, or if publication or
  data artifacts appear.

### Changed

- H1's primary feasibility statistic is pooled out-of-fold balanced accuracy under
  bidirectional cross-mention LODO transfer. AUROC is secondary; matched groups are
  the bootstrap unit. The historical B/C statistic is non-deciding.
- H2 is a separate gate comparing hidden-state and frozen prompt-embedding models
  on identical splits, held-out items, and training-only selection boundary, both
  predicting the **same** target: the four response-strategy superclasses, with the
  nine fine labels secondary. Held-out response-strategy log-loss is primary, under
  the paired estimand `delta_H2` above; the balanced-accuracy difference is
  secondary with the same sign (hidden state minus prompt embedding). H2 inference
  is withheld if the response-label reliability gate fails, and Mini-0 can support
  only single-axis H2 feasibility. Prompt-embedding selection — model, immutable
  revision, license, pooling rule, truncation rule, and maximum input length —
  remains an explicit author decision that blocks `run_ready`.
- H2 hidden states independently select `(layer, C)` while prompt embeddings select
  their own `C` on the same folds, target, items, and log-loss objective. Single-class
  inner/final fits and unrecoverable convergence failures make the affected outer
  fold `NOT_ESTIMABLE`; probability columns are aligned to the fixed class order,
  zero-filled for unseen training classes, then identically clipped/renormalized.
- The response-label gate now requires two humans: the primary labels all responses;
  the independent second labels the frozen 30% group subset. Pre-adjudication
  Cohen's kappa must be at least 0.60, with raw agreement, confusion matrix, class
  counts, and matched-group bootstrap CI reported; failure withholds H2 and H3.
- Manifest compatibility now includes `experiment_id` and `stimulus_file_hash`,
  with each field named exactly once and with timestamp, output directory, shard
  identity, and seed still intentionally excluded. Scientific manifests require
  full 40-character lowercase hexadecimal commit revisions and an explicitly
  formatted `sha256:<64 hex>` stimulus hash; a technical smoke run that uses no
  prompt-embedding model records those fields as `NOT_APPLICABLE_TECHNICAL_SMOKE`
  instead of inventing a frozen revision.
- Mini-0 blocks on its exact layer/position grid and H1 sensitivity raw-p procedure.
  The H3 intervention grid remains visible but is enforced only by the later H3
  stage gate, not by Mini-0.
- TF-IDF is diagnostic under cross-mention transfer and secondary under ordinary
  LODO, not the primary H2 comparator.
- Run-ready QA now records observed factor values and exact confirmation that the
  other two primary axes are absent; partial v0.1.1 QA remains draft-readable only.
- Multiple-comparison families are named separately for H1, H2, H3, and the family
  test, and each applicable family now names the raw-p-value procedure BH operates
  on. Unresolved layer/position/intervention grids remain visible decision blocks.
- Raw effect estimates and raw confidence intervals are reported separately from
  BH-adjusted q-values, and no document any longer labels an ordinary interval as
  though BH had already been applied to it. The
  archived v0.1.1 "after FDR" wording for family components A/B/C is preserved
  unchanged; v0.1.2 records the conflict openly and implements the narrowest
  clarification — the raw interval must lie beyond zero **and** the component's
  BH-adjusted one-sided raw p-value must satisfy `q = 0.05` once a future run plan
  defines it.
- The machine-readable family rule is component-specific: A's raw interval is below
  zero; B's and C's are above zero; all three separately require their BH-adjusted
  one-sided raw p-values. The stale one-sign generic rule was removed.
- Repository versions advance to 0.1.2 on this branch; top-level CFF type is
  corrected to `software`, while the preferred paper citation remains a report.

### Scientific rationale

On cells B and C, task-state and concept-mention labels are exact complements.
Comparing each probe's accuracy against its own labels yields zero both for two
perfect probes and for two chance probes, so the statistic cannot identify the
intended dissociation. Cross-mention transfer tests whether task-state decoding
survives concept-level change without conflating H1 with H2 incremental value.

### Unchanged

- H1–H4 statements, the 2×2 design, three primary axes, four domains, response
  taxonomy, direction derivation, lexical/competence controls, and the family
  decision **A ∧ B ∧ C**.
- Historical tags, GitHub releases, Zenodo records, concept DOI
  `10.5281/zenodo.21294932`, v0.1.0 DOI `10.5281/zenodo.21294933`, and v0.1.1 DOI
  `10.5281/zenodo.21335529`.
- No H5, holonomy, LEM, dialogue-loop, path-dependence, or user-signature content.

### No-data declaration

- No dataset, model run, model response, activation, intervention, statistic, or
  scientific result was produced. The only tokenizer inspection used disposable
  strings and loaded no model weights.

## [0.1.1] — 2026-07-12 (pre-data amendment)

A transparent pre-data amendment of the archived v0.1.0 preregistration. **No data
have been collected**; no model has been run; no results exist. All changes were
made before the first data collection and are documented in
`preregistration/amendment-v0.1.1.md`.

### Review completion status
- v0.1.1 went through **two pre-data correction cycles** (see
  `preregistration/v0.1.1-review-status.md`).
- The **family claim now requires A ∧ B ∧ C** together (shared-vs-separate model,
  behavioral specificity, incremental contribution) — several individual decodable
  directions are not sufficient.
- Stimulus QA is **technically enforced** as a `run_ready` gate before any run.
- **No dataset and no results exist.**
- Test suite: **70 passing**.

### Release
- The preprint was **compiled** (`paper/preprint.pdf`, 11 pages; tectonic).
- PR #1 was **merged to `main`** and v0.1.1 **released on GitHub** (tag `v0.1.1`),
  release date 2026-07-13.
- v0.1.1 is **archived on Zenodo** as a new version under the existing concept
  record: version DOI **`10.5281/zenodo.21335529`**. The concept DOI
  `10.5281/zenodo.21294932` and the v0.1.0 version DOI `10.5281/zenodo.21294933`
  are unchanged. v0.1.0 remains untouched.
- The `v0.1.1` tag and its release asset are the pre-DOI archival build; the DOI was
  added to `README.md`, `CITATION.cff`, and `paper/` in a follow-up
  `record v0.1.1 zenodo doi` commit, and the tag is intentionally left unmoved.

### Added
- `preregistration/amendment-v0.1.1.md`: the pre-data amendment note.
- Preregistered **family-structure test** (shared low-rank vs separate models,
  structured behavioral specificity, incremental shared contribution) in
  `analysis-plan.md`.
- Fixed **primary direction-derivation** rule (regularized logistic regression;
  normalized difference-in-means intervention direction from training groups with
  the concept-mention factor balanced) in `controls-and-baselines.md`.
- Binding **concept-mention (B/D) stimulus-QA protocol** and a **modular mini-shard
  protocol** with immutable run manifests in `experimental-design.md`.
- Two-tier **response-strategy taxonomy**: four primary superclasses mapping the
  nine retained fine labels, in `response-strategy-taxonomy.md` and in
  `ascr.strategy_labels`.
- Seven primary-source-verified prior-art works and matching baselines
  (prompt-embedding and difficulty-representation baselines elevated to primary).
- Code + tests: `RunManifest`, QA metadata, superclass mapping, config-version,
  replication-model and placeholder-revision checks (test suite 29 → 43).
- Earlier in this cycle: Zenodo identifiers and DOI badge for v0.1.0 (concept DOI
  `10.5281/zenodo.21294932`, v0.1.0 version DOI `10.5281/zenodo.21294933`).

### Changed
- Version strings to `0.1.1` across `pyproject.toml`, `CITATION.cff`,
  `.zenodo.json`, `README.md`, and the paper.
- README status to `v0.1.1 pre-data amendment` with a visible amendment link.
- The permissive v0.1.0 "logistic regression / ridge / LDA as candidates" phrasing
  is superseded by a single primary direction-derivation rule (documented, not
  silent).
- The replication model is constrained to differ from the primary model; the config
  placeholder is now `TO_BE_SELECTED_BEFORE_CONFIRMATORY_REPLICATION`.

### Scientific rationale
- The central sharpening: demonstrating several individual task-state directions is
  **not** evidence of a shared ASCR control family. v0.1.1 defines, before data
  collection, the additional evidence required for the family claim, and tightens
  the novelty boundary against newly verified prior art.

### Unchanged
- The archived **v0.1.0 GitHub release, its Git tag, and its Zenodo record** remain
  exactly as published; v0.1.0 is not overwritten or re-tagged.
- The core hypotheses **H1–H4**, the 2×2 design, the three primary axes, the four
  domains, the non-claims, and the mandatory lexical-geometry/competence controls
  are unchanged. No holonomy hypothesis, no "H5", and no LEM extension were added.

### No-data declaration
- No datasets, activations, model outputs, probe/steering results, figures, or
  statistics exist or were produced. This release tightens the preregistration only.

## [0.1.0] — 2026-07-10

Initial public preregistration draft.

### Added
- Preregistered hypotheses (H1–H4) and framing in `preregistration/hypotheses.md`.
- Full experimental design: the $2\times2$ concept-vs-task factorial, candidate
  axes, domains, model and activation plan (`preregistration/experimental-design.md`).
- Analysis plan with probing, transfer, intervention, and identifiability framing
  (`preregistration/analysis-plan.md`).
- Controls and baselines, including the mandatory lexical-geometry control
  (`preregistration/controls-and-baselines.md`).
- Falsification criteria (`preregistration/falsification-criteria.md`).
- Response-strategy taxonomy (`preregistration/response-strategy-taxonomy.md`).
- LaTeX paper draft (`paper/main.tex`) with a verified-only bibliography
  (`paper/references.bib`).
- Prior-art matrix, novelty statement, and citation-verification log under
  `research/`.
- Design-time Python scaffold (`experiments/src/ascr/`) with typed schemas, the
  design-cell and response-strategy labels, config validation, and passing unit
  tests (`tests/`).
- Pilot configuration (`experiments/configs/pilot.yaml`).
- Dual licensing: MIT for code, CC BY 4.0 for written content.
- Project metadata: `CITATION.cff`, `.zenodo.json`, `AUTHORS.md`.

### Status
- No experimental results, datasets, model runs, or figures are included.
- No release, tag, Zenodo deposit, or DOI has been created for this version.
- Every prior-art item considered for the bibliography has been confirmed against
  a primary source; none remain excluded (see
  `research/citation-verification.md`).
