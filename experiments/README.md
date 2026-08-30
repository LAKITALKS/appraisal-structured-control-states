# Experiments

This directory holds the **v0.1.2 design-time scaffold** for the ASCR pilot. It
does not run any model and contains no datasets, activations, generations, or
results.

## Layout

```
experiments/
├── configs/         # pilot config + unfrozen Mini-0 run-plan template
├── data/            # (empty) pilot prompts will live here; README only for now
├── notebooks/       # (empty) analysis notebooks; README only for now
├── results/         # (empty) probe/intervention outputs; README only for now
└── src/ascr/        # importable package: schemas, labels, config validation
```

## What the scaffold provides

- `ascr.strategy_labels` — the response-strategy taxonomy, the 2x2 design-cell
  labels, and the candidate axes / domains, as the single source of truth.
- `ascr.schema` — a typed, validated `PromptItem`, matched-group validation, and
  config/manifest parsing and run-readiness gates.
- `ascr.splits` — pure metadata planners for both cross-mention directions in all
  outer LODO folds and training-only nested selection.
- `ascr.pooling` — pure token-index and Layer-0 user-content mask/pooling helpers.

## Running the checks

From the repository root:

```bash
python -m pytest
```

The tests validate the schema, taxonomy, H1 split boundaries, Layer-0 masks,
matched-group construction, smoke/scientific separation, metadata, and config.

## Before any data generation

- Obtain author approval for the prompt-embedding comparator, then freeze its
  model, immutable revision, license, pooling, and canonical input rule.
- Freeze exact model and tokenizer revisions plus the Mini-0 layer grid, replacing
  all sentinels in `configs/pilot.yaml` and `configs/mini-0-run-plan.yaml`.
- Author the pilot prompts as matched A/B/C/D groups and validate them with
  the strict v0.1.2 `run_ready` QA gate.
- Keep token position, network layer, prompt-vs-generated state, and design cell
  as distinct recorded fields on every activation row.
- Never combine a `technical_smoke` manifest with an `ASCR-Mini-*`
  `scientific_feasibility` manifest. Smoke artifacts are ineligible for all
  scientific calculations.
