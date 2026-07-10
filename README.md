# Toward Appraisal-Structured Latent Control Representations in Language Models

*A Preregistered Hypothesis and Experimental Design for Task-Induced
Response-Strategy Modulation*

**Short name:** ASCR (a working abbreviation used in this repository; not an
established field term).

**Status:** `v0.1 preregistration draft` — this repository reports **no**
experimental results, datasets, model runs, or figures.

---

## Summary

Recent interpretability work shows that instruction-tuned language models contain
causally efficacious latent directions for specific strategic behaviors — refusal,
abstention, uncertainty reporting, evaluation awareness — largely studied one
behavior at a time. This repository preregisters the hypothesis that several of
these effects may be **special cases** of a more general family of *task-induced,
appraisal-structured latent control representations*: low-dimensional, potentially
correlated representations of the model's **own current task situation** that
partially govern its choice of **response strategy** across semantic domains. It
provides the hypotheses, the experimental design, the analysis and control plan, a
verified prior-art review, and a small tested code scaffold — but no results.

## Central hypothesis

> Existing work suggests that language models contain causally efficacious latent
> directions for specific strategic behaviors such as refusal, abstention,
> uncertainty reporting, and evaluation awareness. We hypothesize that some of
> these effects are special cases of a more general family of task-induced,
> appraisal-structured latent control representations of the current task
> situation. These representations may integrate variables such as signed
> relevance, uncertainty, controllability, norm tension, goal congruence, and
> response pressure, and may partially govern response-strategy selection across
> semantic domains.

The central methodological move is a **dissociation** between:

- **Concept tracking** — the prompt *names or describes* an appraisal-related
  concept while the model's own task stays straightforward; and
- **Task induction** — the model's *own task* actually contains ambiguity,
  incompatible constraints, or low controllability, whether or not it is named.

This is operationalized as a $2\times2$ factorial design (actual task state ×
concept mention).

## What is novel

The novelty status is an honest **novel combination**. The individual components —
refusal/abstention/uncertainty/evaluation-awareness directions, task
representations, appraisal variables, valence/arousal geometry, causal steering —
already exist in prior work. The contribution is their **unifying, falsifiable
synthesis**, plus the concept-vs-task dissociation and a mandatory lexical-geometry
control. See [`research/novelty-statement.md`](research/novelty-statement.md) and
the [`research/prior-art-matrix.md`](research/prior-art-matrix.md).

## What is not claimed

This repository does **not** claim or attempt to establish subjective experience,
feeling, consciousness, sentience, suffering, phenomenal states, biological
equivalence, a contemplative mechanism inside a Transformer, a universal
architecture shared by all language models, or the final correct number of latent
dimensions. "Appraisal" names a set of situation variables and "control" names an
influence on response-strategy selection — both used technically, with no
anthropomorphic commitment. The information-bottleneck formalization is optional.

## Repository map

```
.
├── README.md                      # this file
├── AUTHORS.md                     # sole author
├── CHANGELOG.md
├── CITATION.cff / .zenodo.json    # metadata (author: Lazaros Varvatis only)
├── LICENSE / LICENSE-CODE / LICENSE-CONTENT   # dual license (see below)
├── Makefile / pyproject.toml
├── paper/
│   ├── main.tex                   # the preregistration paper (LaTeX source)
│   ├── references.bib             # verified-only bibliography
│   └── figures/                   # placeholder (no result figures)
├── preregistration/
│   ├── hypotheses.md              # H1–H4
│   ├── experimental-design.md     # 2x2 design, axes, domains, model plan
│   ├── analysis-plan.md           # probes, transfer, identifiability
│   ├── controls-and-baselines.md  # baselines + lexical-geometry control
│   ├── falsification-criteria.md
│   └── response-strategy-taxonomy.md
├── research/
│   ├── prior-art-matrix.md
│   ├── citation-verification.md   # verification log (source of truth)
│   └── novelty-statement.md
├── experiments/
│   ├── configs/pilot.yaml         # intended pilot configuration
│   ├── data/ notebooks/ results/  # placeholders (empty; README only)
│   └── src/ascr/                  # tested design-time scaffold
└── tests/                         # unit tests (all passing)
```

## Planned pilot

A feasibility pilot (not a powered study): three primary axes
(uncertainty/unanswerability, norm tension, controllability/coping) × four domains
(software debugging, scheduling/planning, policy-constrained assistance, document
editing), on an open-weight ~7–9B instruction-tuned model (default
`Qwen/Qwen2.5-7B-Instruct`, with the exact revision hash frozen before data
generation). Interpretable linear probes, leave-one-domain-out transfer, and causal
interventions with matched-norm random/PCA controls. Details in
[`preregistration/experimental-design.md`](preregistration/experimental-design.md).

## Reproducing the checks

```bash
python -m pytest          # run the unit tests
make paper                # build paper/preprint.pdf (requires latexmk)
```

> **Build note:** `paper/preprint.pdf` is the compiled version of
> `paper/main.tex` (latexmk/pdflatex, TeX Live; 9 pages, zero warnings, no
> undefined citations). To rebuild it yourself, run `make paper` with a standard
> LaTeX installation.

## How to cite

Please cite via [`CITATION.cff`](CITATION.cff). Until a reviewed release is made,
cite the repository and commit. A DOI is **pending the first reviewed GitHub
Release** and is not yet assigned; there is intentionally no DOI badge here.

## Author

**Lazaros Varvatis** — Independent Researcher, Berlin, Germany.
Email: [varvatislazaros@gmail.com](mailto:varvatislazaros@gmail.com).
Sole author, creator, and maintainer (see [`AUTHORS.md`](AUTHORS.md)).

## License

Dual-licensed: **code under MIT** ([`LICENSE-CODE`](LICENSE-CODE)); **paper,
preregistration, and written content under CC BY 4.0**
([`LICENSE-CONTENT`](LICENSE-CONTENT)). See [`LICENSE`](LICENSE) for the split.
Copyright © 2026 Lazaros Varvatis.
