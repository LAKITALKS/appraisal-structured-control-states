"""Regression tests for the final independent v0.1.2 pre-release review.

These tests operate only on configuration, manifests, and synthetic prompt
metadata. They never import or execute a model or produce scientific observations.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import replace
from pathlib import Path

import pytest
import yaml
from ascr.schema import (
    MINI0_GATE_STAGE,
    NOT_ESTIMABLE,
    QA_BOOLEAN_FIELDS,
    RESPONSE_LABEL_RELIABILITY_SEED,
    RunManifest,
    ValidationError,
    canonical_stimulus_hash,
    config_can_generate_scientific_data,
    config_run_ready_problems,
    h3_run_ready_problems,
    integrated_pre_run_gate_problems,
    item_from_dict,
    load_mini0_run_plan,
    parse_config,
    parse_mini0_run_plan,
    run_plan_run_ready_problems,
    scientific_run_authorized,
    validate_statistical_specification,
)
from ascr.splits import (
    plan_double_crossed_lodo,
    plan_response_label_reliability_subset,
)
from ascr.strategy_labels import DOMAINS

REPO = Path(__file__).resolve().parents[1]
PILOT = REPO / "experiments/configs/pilot.yaml"
MINI0 = REPO / "experiments/configs/mini-0-run-plan.yaml"
HEX_A = "a" * 40
HEX_B = "b" * 40
HEX_C = "c" * 40
HEX_D = "d" * 40
CHAT_HASH = "sha256:" + "f" * 64


def _qa(task: bool, concept: bool) -> dict[str, object]:
    record: dict[str, object] = {name: True for name in QA_BOOLEAN_FIELDS}
    record.update(
        naturalness_rating=5,
        observed_task_state_present=task,
        observed_concept_mention_present=concept,
        non_target_axes_absent_confirmed={
            "norm_tension": True,
            "controllability": True,
        },
        reviewer_id="stimulus-reviewer-1",
        review_timestamp="2026-09-01T00:00:00Z",
        disposition="pass",
    )
    return record


def _ready_stimuli(groups_by_domain: tuple[int, ...] = (10, 10, 10, 10)):
    items = []
    cells = {
        "A": (False, False),
        "B": (False, True),
        "C": (True, False),
        "D": (True, True),
    }
    for domain, count in zip(DOMAINS, groups_by_domain, strict=True):
        for index in range(count):
            gid = f"unc-{domain}-{index:03d}"
            for cell, (task, concept) in cells.items():
                items.append(
                    item_from_dict(
                        {
                            "item_id": f"{gid}-{cell}",
                            "axis": "uncertainty",
                            "domain": domain,
                            "task_state_present": task,
                            "concept_mention_present": concept,
                            "prompt_text": f"Synthetic pre-data QA item {gid} {cell}",
                            "matched_group_id": gid,
                            "expected_strategy_space": ["clarification_request"],
                            "qa": _qa(task, concept),
                        }
                    )
                )
    return items


def _ready_config():
    data = yaml.safe_load(PILOT.read_text(encoding="utf-8"))
    data["validation_mode"] = "run_ready"
    data["model"]["revision"] = HEX_A
    data["model"]["tokenizer_revision"] = HEX_B
    data["prompt_embedding"].update(
        selection_status="AUTHOR_APPROVED_AND_FROZEN",
        model_name="BAAI/bge-base-en-v1.5",
        revision=HEX_C,
        license="mit",
        pooling_rule="cls_then_l2_normalize",
        truncation_rule="truncate_to_model_max_length",
        max_input_length=512,
    )
    data["activations"]["primary_layer_candidates"] = [0, 8, 16, 24, 28]
    data["activations"]["primary_position_candidates"] = [
        "final_non_padding_prompt_token",
        "mean_pooled_user_content_tokens",
    ]
    data["fdr_families"]["h1_layer_position_sensitivity"].update(
        status="FROZEN_PRE_DATA",
        raw_p_value_procedure={
            "test": "matched_group_task_state_label_swap_randomization_test",
            "permutations": 10000,
            "seed": 20260831,
        },
    )
    return parse_config(data)


def _ready_plan(items):
    data = yaml.safe_load(MINI0.read_text(encoding="utf-8"))
    data.update(
        status="FROZEN_PRE_DATA",
        validation_mode="run_ready",
        experiment_id="ASCR-v012-mini0",
        prompt_set_id="ASCR-Mini-0-prompts",
        prompt_set_version="unc-v1",
        stimulus_file_hash=canonical_stimulus_hash(items),
        model_revision=HEX_A,
        tokenizer_revision=HEX_B,
        prompt_embedding_model="BAAI/bge-base-en-v1.5",
        prompt_embedding_revision=HEX_C,
        prompt_embedding_selection_status="AUTHOR_APPROVED_AND_FROZEN",
        prompt_embedding_license="mit",
        prompt_embedding_pooling_rule="cls_then_l2_normalize",
        prompt_embedding_truncation_rule="truncate_to_model_max_length",
        prompt_embedding_max_input_length=512,
        chat_template="qwen-chatml-v1",
        chat_template_hash=CHAT_HASH,
        code_commit=HEX_D,
        layer_candidates=[0, 8, 16, 24, 28],
        position_candidates=[
            "final_non_padding_prompt_token",
            "mean_pooled_user_content_tokens",
        ],
        remaining_mini0_author_decisions=[],
    )
    data["fdr"]["h1_layer_position_sensitivity"].update(
        status="FROZEN_PRE_DATA",
        raw_p_value_procedure={
            "test": "matched_group_task_state_label_swap_randomization_test",
            "permutations": 10000,
            "seed": 20260831,
        },
    )
    return parse_mini0_run_plan(data)


def _ready_manifest(config, plan) -> RunManifest:
    return RunManifest(
        experiment_id=plan.experiment_id,
        shard_id=plan.shard_id,
        run_kind=plan.run_kind,
        eligible_for_scientific_analysis=plan.eligible_for_scientific_analysis,
        target_axis=plan.target_axis,
        prompt_set_id=plan.prompt_set_id,
        prompt_set_version=plan.prompt_set_version,
        model_name=plan.model_name,
        model_revision=plan.model_revision,
        tokenizer_revision=plan.tokenizer_revision,
        prompt_embedding_model=plan.prompt_embedding_model,
        prompt_embedding_revision=plan.prompt_embedding_revision,
        prompt_embedding_license=plan.prompt_embedding_license,
        prompt_embedding_pooling_rule=plan.prompt_embedding_pooling_rule,
        prompt_embedding_truncation_rule=plan.prompt_embedding_truncation_rule,
        prompt_embedding_max_input_length=plan.prompt_embedding_max_input_length,
        chat_template=plan.chat_template,
        chat_template_hash=plan.chat_template_hash,
        code_commit=plan.code_commit,
        seed=0,
        decoding=config.raw["model"]["decoding"],
        layer=16,
        token_position=plan.token_position,
        stimulus_file_hash=plan.stimulus_file_hash,
        output_directory="experiments/results/ASCR-Mini-0/",
        environment="test-only-no-model",
        timestamp="2026-09-01T00:00:00Z",
    )


def test_authoritative_gate_requires_all_four_compatible_artifacts() -> None:
    items = _ready_stimuli()
    config = _ready_config()
    plan = _ready_plan(items)
    manifest = _ready_manifest(config, plan)

    assert config_run_ready_problems(config, stage=MINI0_GATE_STAGE) == []
    assert config_can_generate_scientific_data(config) is False
    missing = integrated_pre_run_gate_problems(config, items)
    assert any(problem.startswith("run_plan:") for problem in missing)
    assert any(problem.startswith("manifest:") for problem in missing)
    assert (
        integrated_pre_run_gate_problems(
            config, items, run_plan=plan, manifest=manifest
        )
        == []
    )
    assert scientific_run_authorized(config, items, run_plan=plan, manifest=manifest)
    mutable = replace(config, model_revision="main")
    assert any(
        "40-character" in problem for problem in config_run_ready_problems(mutable)
    )
    fake_grid = replace(plan, layer_candidates="16")
    assert any(
        "layer_candidates" in problem
        for problem in run_plan_run_ready_problems(fake_grid)
    )


@pytest.mark.parametrize(
    "change,needle",
    [
        ({"experiment_id": "ASCR-wrong"}, "experiment_id"),
        ({"code_commit": "e" * 40}, "code_commit"),
        ({"chat_template_hash": "sha256:" + "0" * 64}, "chat_template_hash"),
        ({"stimulus_file_hash": "sha256:" + "1" * 64}, "stimulus_file_hash"),
    ],
)
def test_authoritative_gate_rejects_manifest_mismatch(
    change: dict[str, object], needle: str
) -> None:
    items = _ready_stimuli()
    config = _ready_config()
    plan = _ready_plan(items)
    manifest = replace(_ready_manifest(config, plan), **change)
    problems = integrated_pre_run_gate_problems(
        config, items, run_plan=plan, manifest=manifest
    )
    assert any(needle in problem for problem in problems)


def test_canonical_stimulus_hash_is_order_independent_and_content_sensitive() -> None:
    items = _ready_stimuli()
    assert canonical_stimulus_hash(items) == canonical_stimulus_hash(
        list(reversed(items))
    )
    changed = list(items)
    changed[0] = replace(changed[0], prompt_text="Changed before freeze")
    assert canonical_stimulus_hash(changed) != canonical_stimulus_hash(items)


def test_mini0_does_not_require_h3_but_h3_has_its_own_gate() -> None:
    config = _ready_config()
    assert not any("H3" in problem for problem in config_run_ready_problems(config))
    assert any("H3" in problem for problem in h3_run_ready_problems(config))
    pilot = yaml.safe_load(PILOT.read_text(encoding="utf-8"))
    assert (
        "fdr_families.h3_intervention.status"
        not in pilot["run_gate"]["blocking_sentinels"]
    )


def test_mini0_axis_domain_and_balance_constraints_are_enforced() -> None:
    config = _ready_config()
    plan = _ready_plan(_ready_stimuli())

    one_domain = _ready_stimuli((40, 0, 0, 0))
    problems = integrated_pre_run_gate_problems(
        config,
        one_domain,
        run_plan=plan,
        manifest=_ready_manifest(config, plan),
    )
    assert any("all registered domains" in problem for problem in problems)

    unbalanced = _ready_stimuli((13, 9, 9, 9))
    unbalanced_plan = _ready_plan(unbalanced)
    problems = integrated_pre_run_gate_problems(
        config,
        unbalanced,
        run_plan=unbalanced_plan,
        manifest=_ready_manifest(config, unbalanced_plan),
    )
    assert any("evenly distributed" in problem for problem in problems)

    mixed = _ready_stimuli()
    mixed[-4:] = [replace(item, axis="norm_tension") for item in mixed[-4:]]
    with pytest.raises(ValidationError, match="exactly one target axis"):
        plan_double_crossed_lodo(mixed)


def test_h2_independent_selection_and_estimability_are_machine_bound() -> None:
    data = yaml.safe_load(PILOT.read_text(encoding="utf-8"))
    selection = data["analysis"]["hyperparameter_selection"]
    assert selection["h2_hidden_state_selects"] == ["layer", "C"]
    assert selection["h2_prompt_embedding_selects"] == ["C"]
    assert selection["h2_classifiers_select_independently"] is True
    assert selection["smaller_C_tie_break_applied_separately"] is True
    assert selection["earlier_layer_tie_break_applies_to"] == "hidden_state_only"

    estimability = data["analysis"]["h2"]["estimability"]
    assert estimability["single_class_inner_fit_fold"].endswith(NOT_ESTIMABLE)
    assert estimability["single_class_final_outer_fit"].endswith(NOT_ESTIMABLE)
    assert estimability["unconverged_models_may_not_score"] is True
    assert estimability["probability_columns_aligned_before_clipping"] is True
    assert estimability["missing_training_class_probability"] == 0.0

    altered = deepcopy(data)
    altered["analysis"]["hyperparameter_selection"][
        "h2_classifiers_select_independently"
    ] = False
    with pytest.raises(ValidationError):
        validate_statistical_specification(altered)


def test_response_label_reliability_protocol_and_subset_are_operational() -> None:
    items = _ready_stimuli()
    plan = plan_response_label_reliability_subset(items, target_axis="uncertainty")
    assert plan.seed == RESPONSE_LABEL_RELIABILITY_SEED == 20260901
    assert len(plan.selected_group_ids) == 12
    assert dict(plan.selected_groups_per_domain) == {domain: 3 for domain in DOMAINS}
    assert plan == plan_response_label_reliability_subset(
        items, target_axis="uncertainty"
    )
    uneven_total = plan_response_label_reliability_subset(
        _ready_stimuli((11, 10, 10, 10)), target_axis="uncertainty"
    )
    assert len(uneven_total.selected_group_ids) == 13
    counts = tuple(dict(uneven_total.selected_groups_per_domain).values())
    assert max(counts) - min(counts) == 1

    protocol = yaml.safe_load(PILOT.read_text(encoding="utf-8"))["analysis"][
        "response_label_reliability"
    ]
    assert protocol["primary_statistic"] == "cohen_kappa"
    assert protocol["pass_threshold_kappa"] == 0.60
    assert protocol["fewer_than_two_observed_classes"] == "NOT_ESTIMABLE_AND_FAIL"
    assert protocol["failed_gate_action"] == "withhold_H2_and_H3_inference"
    altered = yaml.safe_load(PILOT.read_text(encoding="utf-8"))
    altered["analysis"]["response_label_reliability"]["pass_threshold_kappa"] = 0.50
    with pytest.raises(ValidationError):
        validate_statistical_specification(altered)


def test_family_rules_are_component_specific_and_stale_rule_is_absent() -> None:
    pilot = yaml.safe_load(PILOT.read_text(encoding="utf-8"))
    family = pilot["family_structure_test"]
    assert "decision_rule" not in family
    assert family["decision_logic"] == "A_and_B_and_C"
    assert family["component_rules"]["A_shared_vs_separate"][
        "raw_interval_condition"
    ].endswith("below_zero")
    for component in ("B_behavioral_specificity", "C_incremental"):
        assert family["component_rules"][component]["raw_interval_condition"].endswith(
            "above_zero"
        )
    altered = deepcopy(pilot)
    altered["family_structure_test"]["component_rules"]["A_shared_vs_separate"][
        "raw_interval_condition"
    ] = "raw_95pct_ci_entirely_above_zero"
    with pytest.raises(ValidationError):
        validate_statistical_specification(altered)
    current_text = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (
            PILOT,
            REPO / "experiments/src/ascr/schema.py",
            REPO / "preregistration/analysis-plan.md",
        )
    )
    assert "paired_matched_group_bootstrap_ci_below_zero_after_fdr" not in current_text


def test_seed_policy_does_not_claim_seeded_lodo_splits() -> None:
    pilot = yaml.safe_load(PILOT.read_text(encoding="utf-8"))
    assert (
        "matched_group_splits"
        not in pilot["temperature_zero_generation_policy"]["seeds_govern"]
    )
    assert pilot["analysis"]["split_assignments_depend_on_seed"] is False


def test_committed_mini0_template_is_parseable_but_fail_closed() -> None:
    plan = load_mini0_run_plan(MINI0)
    assert plan.status == "PRE_DATA_UNFROZEN"
    assert plan.validation_mode == "draft"
    assert plan.remaining_mini0_author_decisions
