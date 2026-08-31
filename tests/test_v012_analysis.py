"""Pre-data tests for the v0.1.2 H1 split, Layer-0, and smoke boundaries."""

from __future__ import annotations

import pathlib

import pytest
import yaml
from ascr.pooling import (
    final_non_padding_index,
    mean_pool_user_content_embeddings,
    user_content_pool_mask,
)
from ascr.schema import (
    PromptItem,
    RunManifest,
    ValidationError,
    item_from_dict,
    manifests_compatible,
)
from ascr.splits import (
    CONCEPT_ABSENT_TO_PRESENT,
    CONCEPT_PRESENT_TO_ABSENT,
    plan_double_crossed_lodo,
    plan_inner_selection_folds,
)
from ascr.strategy_labels import DOMAINS

REPO = pathlib.Path(__file__).resolve().parents[1]


def _stimuli(groups_per_domain: int = 2) -> list[PromptItem]:
    items: list[PromptItem] = []
    cells = {
        "A": (False, False),
        "B": (False, True),
        "C": (True, False),
        "D": (True, True),
    }
    for domain in DOMAINS:
        for group_index in range(groups_per_domain):
            gid = f"unc-{domain}-{group_index:02d}"
            for cell, (task, concept) in cells.items():
                items.append(
                    item_from_dict(
                        {
                            "item_id": f"{gid}-{cell}",
                            "axis": "uncertainty",
                            "domain": domain,
                            "task_state_present": task,
                            "concept_mention_present": concept,
                            "prompt_text": f"Disposable design item {gid} {cell}",
                            "matched_group_id": gid,
                            "expected_strategy_space": ["clarification_request"],
                        }
                    )
                )
    return items


def test_old_bc_accuracy_difference_is_non_identifying() -> None:
    # Perfect task and concept probes each score 1 against their own complementary
    # labels, exactly as two chance-level probes can have equal scores.
    perfect_difference = 1.0 - 1.0
    chance_difference = 0.5 - 0.5
    assert perfect_difference == chance_difference == 0.0


def test_double_crossed_lodo_has_all_domains_and_both_directions() -> None:
    folds = plan_double_crossed_lodo(_stimuli())
    assert len(folds) == 8
    assert {fold.test_domain for fold in folds} == set(DOMAINS)
    assert {fold.direction for fold in folds} == {
        CONCEPT_ABSENT_TO_PRESENT,
        CONCEPT_PRESENT_TO_ABSENT,
    }


def test_outer_folds_keep_matched_groups_on_one_side() -> None:
    for fold in plan_double_crossed_lodo(_stimuli()):
        assert set(fold.training_group_ids).isdisjoint(fold.test_group_ids)
        assert set(fold.training_item_ids).isdisjoint(fold.test_item_ids)
        assert all(fold.test_domain not in gid for gid in fold.training_group_ids)
        assert all(fold.test_domain in gid for gid in fold.test_group_ids)


def test_double_crossed_cell_directions_are_correct() -> None:
    folds = plan_double_crossed_lodo(_stimuli())
    absent = next(f for f in folds if f.direction == CONCEPT_ABSENT_TO_PRESENT)
    present = next(f for f in folds if f.direction == CONCEPT_PRESENT_TO_ABSENT)
    assert absent.training_cells == ("A_neutral_control", "C_pure_task_induction")
    assert absent.test_cells == ("B_concept_tracking_only", "D_combined")
    assert present.training_cells == ("B_concept_tracking_only", "D_combined")
    assert present.test_cells == ("A_neutral_control", "C_pure_task_induction")


def test_inner_selection_never_receives_outer_test_domain() -> None:
    items = _stimuli(groups_per_domain=2)
    outer = plan_double_crossed_lodo(items)[0]
    inner = plan_inner_selection_folds(items, outer)
    by_id = {item.item_id: item for item in items}
    assert len(inner) == 3  # inner leave-one-training-domain-out
    for fold in inner:
        selected_ids = fold.training_item_ids + fold.validation_item_ids
        assert all(
            by_id[item_id].domain != outer.test_domain for item_id in selected_ids
        )
        assert set(fold.training_group_ids).isdisjoint(fold.validation_group_ids)
        assert fold.inner_validation_domain != outer.test_domain


def test_layer_zero_mask_excludes_template_special_and_padding_tokens() -> None:
    # system, user-marker, user-1, user-2, special-end, assistant-prefix, padding
    mask = user_content_pool_mask(
        user_content_mask=[0, 0, 1, 1, 0, 0, 0],
        attention_mask=[1, 1, 1, 1, 1, 1, 0],
        special_tokens_mask=[0, 1, 0, 0, 1, 1, 1],
    )
    assert mask == (False, False, True, True, False, False, False)
    pooled = mean_pool_user_content_embeddings(
        token_embeddings=[
            [100.0, 100.0],
            [200.0, 200.0],
            [1.0, 3.0],
            [3.0, 5.0],
            [300.0, 300.0],
            [400.0, 400.0],
            [500.0, 500.0],
        ],
        user_content_mask=[0, 0, 1, 1, 0, 0, 0],
        attention_mask=[1, 1, 1, 1, 1, 1, 0],
        special_tokens_mask=[0, 1, 0, 0, 1, 1, 1],
    )
    assert pooled == (2.0, 4.0)


def test_final_non_padding_index_handles_right_and_left_padding() -> None:
    assert final_non_padding_index([1, 1, 1, 0, 0]) == 2
    assert final_non_padding_index([0, 0, 1, 1, 1]) == 4
    with pytest.raises(ValidationError):
        final_non_padding_index([0, 0])


def _manifest(**overrides: object) -> RunManifest:
    data: dict[str, object] = {
        "experiment_id": "ASCR-v012",
        "shard_id": "ASCR-Mini-0",
        "run_kind": "scientific_feasibility",
        "eligible_for_scientific_analysis": True,
        "target_axis": "uncertainty",
        "prompt_set_id": "ASCR-Mini-0-prompts",
        "prompt_set_version": "unc-v1",
        "model_name": "Qwen/Qwen2.5-7B-Instruct",
        "model_revision": "a" * 40,
        "tokenizer_revision": "b" * 40,
        "prompt_embedding_model": "BAAI/bge-base-en-v1.5",
        "prompt_embedding_revision": "c" * 40,
        "prompt_embedding_license": "mit",
        "prompt_embedding_pooling_rule": "cls_then_l2_normalize",
        "prompt_embedding_truncation_rule": "truncate_to_model_max_length",
        "prompt_embedding_max_input_length": 512,
        "chat_template": "qwen-chatml",
        "chat_template_hash": "sha256:" + "f" * 64,
        "code_commit": "d" * 40,
        "seed": 0,
        "decoding": {"temperature": 0.0},
        "layer": 16,
        "token_position": "prompt_final_non_padding",
        "stimulus_file_hash": "sha256:" + "e" * 64,
        "output_directory": "experiments/results/ASCR-Mini-0/",
        "environment": "test-only",
        "timestamp": "2026-08-30T00:00:00Z",
    }
    data.update(overrides)
    return RunManifest(**data)  # type: ignore[arg-type]


def test_smoke_manifest_is_structurally_incompatible_with_mini0() -> None:
    scientific = _manifest()
    smoke = _manifest(
        shard_id="ASCR-Technical-Smoke-0",
        run_kind="technical_smoke",
        eligible_for_scientific_analysis=False,
        prompt_set_id="DISPOSABLE_TOKENIZER_SMOKE",
        prompt_set_version="smoke-v1",
        output_directory="experiments/results/technical-smoke/run-0/",
    )
    scientific.validate(require_frozen_revision=True)
    smoke.validate(require_frozen_revision=True)
    assert not manifests_compatible(scientific, smoke)


def test_smoke_manifest_cannot_claim_scientific_eligibility() -> None:
    bad = _manifest(
        shard_id="ASCR-Technical-Smoke-0",
        run_kind="technical_smoke",
        eligible_for_scientific_analysis=True,
        prompt_set_id="DISPOSABLE_SMOKE",
        output_directory="experiments/results/technical-smoke/",
    )
    with pytest.raises(ValidationError):
        bad.validate()


def test_pilot_config_declares_exact_h1_and_h2_fdr_families() -> None:
    cfg = yaml.safe_load((REPO / "experiments/configs/pilot.yaml").read_text())
    families = cfg["fdr_families"]
    assert families["h1_primary_aggregate"]["correction"].startswith("none_")
    assert families["h2_primary_aggregate"]["sign_convention"] == (
        "positive_favors_hidden_state"
    )
    assert len(families["h1_direction_domain_secondary"]["members"]) == 16
    assert len(families["h2_direction_domain_secondary"]["members"]) == 8
    assert families["family_structure_primary"]["members"] == [
        "A_shared_minus_separate_pooled_log_loss",
        "B_strategy_selectivity_contrast",
        "C_incremental_response_strategy_log_loss",
    ]
