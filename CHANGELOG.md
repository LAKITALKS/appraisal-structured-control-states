# Changelog

All notable changes to this repository are documented here. This project follows
[Semantic Versioning](https://semver.org/) for its metadata version field.

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
