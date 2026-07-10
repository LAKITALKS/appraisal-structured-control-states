# Experiments

This directory holds the **design-time scaffold** for the ASCR pilot. It does not
run any model, and it contains no datasets or results yet.

## Layout

```
experiments/
├── configs/         # pilot.yaml: the intended pilot configuration
├── data/            # (empty) pilot prompts will live here; README only for now
├── notebooks/       # (empty) analysis notebooks; README only for now
├── results/         # (empty) probe/intervention outputs; README only for now
└── src/ascr/        # importable package: schemas, labels, config validation
```

## What the scaffold provides

- `ascr.strategy_labels` — the response-strategy taxonomy, the 2x2 design-cell
  labels, and the candidate axes / domains, as the single source of truth.
- `ascr.schema` — a typed, validated `PromptItem`, matched-group validation, and
  config parsing/loading.

## Running the checks

From the repository root:

```bash
python -m pytest
```

The tests validate the schema, the label vocabulary, matched-group construction,
and that `configs/pilot.yaml` parses.

## Before any data generation

- Freeze the exact model revision hash in `configs/pilot.yaml`
  (`model.revision`), replacing the sentinel value.
- Author the pilot prompts as matched A/B/C/D groups and validate them with
  `ascr.schema.validate_matched_group`.
- Keep token position, network layer, prompt-vs-generated state, and design cell
  as distinct recorded fields on every activation row.
