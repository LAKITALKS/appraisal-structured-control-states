# Changelog

All notable changes to this repository are documented here. This project follows
[Semantic Versioning](https://semver.org/) for its metadata version field.

## [0.1.1] — 2026-07-12 (pre-data amendment)

A transparent pre-data amendment of the archived v0.1.0 preregistration. **No data
have been collected**; no model has been run; no results exist. All changes were
made before the first data collection and are documented in
`preregistration/amendment-v0.1.1.md`.

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
