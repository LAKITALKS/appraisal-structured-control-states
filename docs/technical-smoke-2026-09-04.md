# Non-scientific Technical Smoke — 2026-09-04

## Status and scope

One bounded ASCR Technical Smoke completed successfully on 2026-09-04. Its sole
purpose was to test the engineering path from pinned input and chat-template
processing through hidden-state extraction, pooling, serialization, return to the
local caller, and manifest construction.

This was **not** Mini-0, a feasibility result, or a scientific ASCR run. It used
eight disposable prompts, performed no text generation or intervention, and did
not test H1, H2, or any other ASCR claim. The artifacts carry
`eligible_for_scientific_analysis: false` and must not enter a scientific dataset,
statistic, figure, or conclusion. The planned 7B model/tokenizer revision, Mini-0
layer/position grid, and scientific run plan remain unfrozen.

## Executed configuration

| Item | Verified run record |
| --- | --- |
| Execution | Modal, CPU only (`x86_64`) |
| Configured resources | 4 CPU, 8,192 MiB memory, no GPU |
| Model | `Qwen/Qwen2.5-0.5B-Instruct` |
| Model and tokenizer revision | `7ae557604adf67be50417f59c2c2f167def9a775` |
| Tokenizer | `Qwen2TokenizerFast`, right padding |
| Executed code commit | `9cb1515e242ed974f15bedd1a25b03d60d338b1e` |
| Run directory ID | `run-20260904T130643Z-9cb1515e242e` |
| Prompt set | `DISPOSABLE_SMOKE_01`, version `1`, eight prompts |
| Remote environment | Python 3.11.12; torch 2.7.1+cpu; transformers 4.53.2; safetensors 0.5.3 |
| Recorded execution window | 2026-09-04 13:06:52–13:07:09 UTC (17.517865925 s) |

The original console log reaches all eleven stage markers, from
`request_verified` through `manifests_built`, then records normal Modal completion
and `PASS: one technical smoke artifact set written locally`. The log establishes
that PASS path; at executed commit `9cb1515e…`, the path returns process exit code
0. A separate shell-status record was not archived, and the exit code is not a
field in either manifest or `summary.json`.

## Technical results

The following values are read from the original local `summary.json` and the two
manifests unless a separate recalculation is identified below.

- `status`: `PASS_TECHNICAL_SMOKE`.
- Eight prompts were tokenized in one right-padded batch with recorded sequence
  length 37.
- The model returned 25 hidden states: the embedding state plus 24 Transformer
  layers. The reported per-state shape was `[8, 37, 896]`, with dtype `float32`.
- Stored readouts were `layer_0_user_content_mean` and
  `layer_12_final_non_padding`, each with shape `[8, 896]` and dtype `float32`.
- The independent float64 pooling reference had maximum absolute error `0.0`.
- The guarded serialization round trip was exact.
- Two manifests were constructed, for layers 0 and 12 with distinct token-position
  fields.
- `generation_performed` and `causal_lm_head_executed` were both `false`.
- `scientific_analysis_eligible` was `false`.

## Original evidence and independent checks

The original artifact directory was available locally at verification time as:

`experiments/results/technical-smoke/run-20260904T130643Z-9cb1515e242e/`

It contained only `summary.json`, two layer manifests, and `tensors.pt`. These
runtime files are not included in this documentation commit. At executed commit
`9cb1515e…`, the complete `experiments/results/technical-smoke/` tree was explicitly
Git-ignored.

| Original file | Bytes recalculated 2026-09-06 | File SHA-256 recalculated 2026-09-06 |
| --- | ---: | --- |
| `summary.json` | 2,126 | `6b7807380e11078683bdd4c44d66b552ff64489e96f7b33cd3026bf3e648c5aa` |
| `manifest-layer-00.json` | 2,483 | `55cd503c3b7408912ad4acbc9f1e34985d077658333a3234da8e883559f1bc23` |
| `manifest-layer-12.json` | 2,491 | `23990efce4f5e2b97a859ec4f53b430188691cf6eaa1735f9835c7961fbbdf38` |
| `tensors.pt` | 59,173 | `af164bb127f5469fa4a8a7e0bbe88ed3c9771ad83c99ee4d3239fd600b582d4c` |

The recalculated tensor size and hash match `archive_bytes: 59173` and
`archive_hash` in `summary.json`. In addition, all eight hashes in the preserved preflight
`source_hashes` mapping were recalculated from the corresponding Git blobs at
`9cb1515e…`; all eight matched. The recorded `config_hash` also matched the
configuration blob. Hardware, package versions, resolved revisions, tensor
properties, pooling error, timestamps, duration, and run status are run-recorded
metadata and were not independently recomputed by this documentation update. The
chat-template hash was not re-derived because that would require loading the
pinned tokenizer; no model or tokenizer was loaded for this update.

## Manifest excerpts

These are **excerpts** using the original schema field names, not complete
manifests:

```json
{
  "code_commit": "9cb1515e242ed974f15bedd1a25b03d60d338b1e",
  "eligible_for_scientific_analysis": false,
  "model_name": "Qwen/Qwen2.5-0.5B-Instruct",
  "model_revision": "7ae557604adf67be50417f59c2c2f167def9a775",
  "tokenizer_revision": "7ae557604adf67be50417f59c2c2f167def9a775",
  "chat_template": "Qwen/Qwen2.5-0.5B-Instruct:tokenizer_config.json@7ae557604adf67be50417f59c2c2f167def9a775",
  "chat_template_hash": "sha256:cd8e9439f0570856fd70470bf8889ebd8b5d1107207f67a5efb46e342330527f",
  "run_kind": "technical_smoke",
  "target_axis": "none_technical_smoke",
  "prompt_set_id": "DISPOSABLE_SMOKE_01",
  "stimulus_file_hash": "sha256:c3e3a6da287dde6b97de9bce698a54ffffd8dafea51a10bc391c3c2f92139abb"
}
```

Layer-specific excerpts:

```json
{ "layer": 0, "token_position": "user_content_mean" }
{ "layer": 12, "token_position": "prompt_final_non_padding" }
```

The recorded decoding object also contains
`"mode": "forward_only_no_generation"`,
`"output_hidden_states": true`, and
`"causal_lm_head_executed": false`.

## Code provenance and remaining limitation

The smoke actually ran at `9cb1515e242ed974f15bedd1a25b03d60d338b1e`.
The later local engineering commit
`749b1983f30a5eeeaa8dfe44c490f62229359232` adds a static regression test for
library-derived string coercions and observability designed to record which mounted
module files and `sys.path` entries execute remotely. That code was not used by the
recorded run and has **not** been run again in Modal. Its `module_provenance` output
therefore remains unobserved, and this report makes no cloud-verification claim for
`749b1983…`.

At the time this documentation was prepared, both implementation commits existed
only on local branches. The current public `main` commit was
`34ec043a119bc824c97346982d456b0f87b53cb4`; neither `9cb1515e…` nor `749b1983…`
was contained in a remote branch. This documentation-only change is based directly
on that public `main` state and deliberately does not include the unpublished
engineering diff or any runtime artifact. Repository:
[LAKITALKS/appraisal-structured-control-states](https://github.com/LAKITALKS/appraisal-structured-control-states).

## Interpretation boundary

The successful smoke supports only the narrow claim that this pinned 0.5B CPU
execution traversed the recorded technical path and returned internally consistent
artifacts. It provides no evidence for latent appraisal structure, cross-domain
transfer, response-strategy prediction, causal control, H1, H2, or any broader ASCR
hypothesis. No rerun was performed to prepare this report.
