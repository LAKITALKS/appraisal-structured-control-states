# Experiments

This directory holds the **v0.1.2 design-time scaffold** for the ASCR pilot. It
contains no scientific model-run data, activation datasets, generations,
interventions, or results. A separate, deliberately non-scientific Technical Smoke
completed on 2026-09-04; it did not run Mini-0 and its disposable artifacts are
ineligible for scientific analysis. See the
[technical report](../docs/technical-smoke-2026-09-04.md).

## Layout

```
experiments/
├── configs/         # pilot config + unfrozen Mini-0 run-plan template
├── data/            # (empty) pilot prompts will live here; README only for now
├── notebooks/       # (empty) analysis notebooks; README only for now
├── results/         # no scientific probe/intervention outputs
└── src/ascr/        # importable package: schemas, labels, config validation
```

## Technical Smoke record

The successful CPU smoke exercised tokenization, chat-template application,
hidden-state extraction, pooling, serialization, and manifest construction with
eight disposable prompts and `Qwen/Qwen2.5-0.5B-Instruct`. No generation or
causal-LM-head execution occurred. The local smoke implementation and ignored
runtime artifacts are not part of this documentation-only branch or of the public
`main` state against which it was prepared; the report records the exact executed
commit and publication boundary.

## What the scaffold provides

- `ascr.strategy_labels` — the response-strategy taxonomy, the 2x2 design-cell
  labels, and the candidate axes / domains, as the single source of truth.
- `ascr.schema` — a typed, validated `PromptItem`, matched-group validation, and
  config/manifest parsing and run-readiness gates.
- `ascr.splits` — pure metadata planners for both cross-mention directions in all
  outer LODO folds, the inner leave-one-training-domain-out selection folds, and
  the domain-stratified matched-group cluster-bootstrap and second-labeler subset
  plans. These planners return identifiers only; they compute no statistic and
  touch no model output.
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
  model, immutable revision, license, pooling rule, truncation/input rule, and
  maximum input length.
- Freeze exact model and tokenizer revisions plus the Mini-0 layer and position
  grids, replacing all sentinels in `configs/pilot.yaml` and
  `configs/mini-0-run-plan.yaml`. Scientific manifests require full 40-character
  lowercase hexadecimal commit revisions.
- Construct the immutable `RunManifest`, load the frozen `Mini0RunPlan`, then call
  `ascr.schema.integrated_pre_run_gate_problems(config, items, run_plan=plan,
  manifest=manifest)` and require an empty result **before** constructing,
  downloading, or loading any model. Configuration-only and stimulus-only helpers
  are diagnostic guards and can never authorize scientific model construction.
- Confirm that all Mini-0 items use the uncertainty axis, cover all four registered
  domains with complete-group counts differing by at most one, and that the
  canonical typed-item SHA-256 matches both plan and manifest.
- Author the pilot prompts as matched A/B/C/D groups and validate them with
  the strict v0.1.2 `run_ready` QA gate.
- Keep token position, network layer, prompt-vs-generated state, and design cell
  as distinct recorded fields on every activation row.
- Never combine a `technical_smoke` manifest with an `ASCR-Mini-*`
  `scientific_feasibility` manifest. Smoke artifacts are ineligible for all
  scientific calculations.
