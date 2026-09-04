"""Regression guards for the frozen v0.1.2 statistical and release specification.

Every test here fails if a registered pre-data choice silently changes: the H2
target and class vocabulary, the H2 log-loss sign convention and decision rules,
the H1/H2 target separation, the probe pipeline and regularization grid, the
selection tie-breaking, the seed roles, the inner leave-one-training-domain-out
structure, the cluster-bootstrap algorithm, the Benjamini-Hochberg raw-p-value
procedure, the manifest guards, the canonical PDF build, and the no-data /
archived-with-version-DOI status of this version.

No model is run and no data are produced by any test in this file.
"""

from __future__ import annotations

import pathlib
import re

import ascr
import pytest
import yaml
from ascr.schema import (
    _MANIFEST_COMPAT_FIELDS,
    _MANIFEST_EXCLUDED_COMPAT_FIELDS,
    BH_Q,
    BOOTSTRAP_SEED,
    H1_TARGET,
    H2_PRIMARY_ESTIMAND,
    H2_SECONDARY_SIGN_CONVENTION,
    H2_SIGN_CONVENTION,
    H2_TARGET,
    NOT_APPLICABLE_TECHNICAL_SMOKE,
    NOT_ESTIMABLE,
    PERMUTATION_SEED,
    PRIMARY_SEED,
    REGULARIZATION_C_GRID,
    SENSITIVITY_SEEDS,
    PromptItem,
    RunManifest,
    ValidationError,
    integrated_pre_run_gate_problems,
    item_from_dict,
    load_config,
    manifests_compatible,
    parse_config,
    scientific_run_authorized,
    validate_statistical_specification,
)
from ascr.splits import (
    BOOTSTRAP_RESAMPLES,
    CONCEPT_ABSENT_TO_PRESENT,
    INNER_LODO_FOLDS,
    PERMUTATION_REPLICATES,
    held_out_groups_by_domain,
    plan_cluster_bootstrap,
    plan_double_crossed_lodo,
    plan_inner_selection_folds,
)
from ascr.strategy_labels import DOMAINS, STRATEGY_SUPERCLASSES

REPO = pathlib.Path(__file__).resolve().parents[1]
PILOT = REPO / "experiments/configs/pilot.yaml"
MINI0 = REPO / "experiments/configs/mini-0-run-plan.yaml"


def _pilot() -> dict:
    return yaml.safe_load(PILOT.read_text(encoding="utf-8"))


def _stimuli(groups_per_domain: int = 3) -> list[PromptItem]:
    items: list[PromptItem] = []
    cells = {
        "A": (False, False),
        "B": (False, True),
        "C": (True, False),
        "D": (True, True),
    }
    for domain in DOMAINS:
        for index in range(groups_per_domain):
            gid = f"unc-{domain}-{index:02d}"
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


# --------------------------------------------------------------------------- #
# H2 target, sign convention, decision rules, and H1/H2 separation
# --------------------------------------------------------------------------- #
def test_h2_target_is_registered_and_matches_config() -> None:
    h2 = _pilot()["analysis"]["h2"]
    assert H2_TARGET == "response_strategy_superclass"
    assert h2["target"] == H2_TARGET
    assert h2["fine_label_role"] == "secondary"
    assert h2["label_reliability_gate_blocks_inference"] is True
    assert h2["same_target_and_items_for_both_classifiers"] is True


def test_h2_class_vocabulary_is_the_four_fixed_superclasses() -> None:
    h2 = _pilot()["analysis"]["h2"]
    assert tuple(h2["target_classes"]) == STRATEGY_SUPERCLASSES
    assert STRATEGY_SUPERCLASSES == (
        "direct_or_comply",
        "qualify_or_warn",
        "redirect_or_clarify",
        "decline_or_abstain",
    )


def test_h1_and_h2_targets_are_not_conflated() -> None:
    analysis = _pilot()["analysis"]
    assert analysis["h1"]["target"] == H1_TARGET == "task_state_present"
    assert analysis["h2"]["target"] != analysis["h1"]["target"]
    data = _pilot()
    data["analysis"]["h2"]["target"] = "task_state_present"
    with pytest.raises(ValidationError):
        validate_statistical_specification(data)


def test_h2_log_loss_sign_convention_is_prompt_embedding_minus_hidden_state() -> None:
    h2 = _pilot()["analysis"]["h2"]
    assert H2_PRIMARY_ESTIMAND == (
        "log_loss_prompt_embedding_minus_log_loss_hidden_state"
    )
    assert h2["primary_estimand"] == H2_PRIMARY_ESTIMAND
    assert h2["sign_convention"] == H2_SIGN_CONVENTION == "positive_favors_hidden_state"
    assert h2["secondary_sign_convention"] == H2_SECONDARY_SIGN_CONVENTION
    assert "hidden_state_minus_prompt_embedding" in H2_SECONDARY_SIGN_CONVENTION


def test_reversed_h2_sign_convention_is_rejected() -> None:
    data = _pilot()
    data["analysis"]["h2"][
        "primary_estimand"
    ] = "log_loss_hidden_state_minus_log_loss_prompt_embedding"
    with pytest.raises(ValidationError):
        validate_statistical_specification(data)


def test_h2_decision_rules_are_present_and_named() -> None:
    h2 = _pilot()["analysis"]["h2"]
    assert "above_0" in h2["positive_rule"]
    assert "at_or_below_0" in h2["weakened_rule"]
    assert "overlaps_0" in h2["indeterminate_rule"]
    for rule in ("positive_rule", "weakened_rule", "indeterminate_rule"):
        data = _pilot()
        del data["analysis"]["h2"][rule]
        with pytest.raises(ValidationError):
            validate_statistical_specification(data)


def test_h2_estimability_rules_are_conservative() -> None:
    est = _pilot()["analysis"]["h2"]["estimability"]
    assert est["single_class_training_fold"] == NOT_ESTIMABLE
    assert est["not_estimable_primary_aggregate_is"] == "indeterminate"
    assert est["post_data_class_merging_forbidden"] is True
    assert est["post_data_fold_domain_direction_dropping_forbidden"] is True
    assert est["silent_exclusion_forbidden"] is True
    clip = est["log_loss_probability_clipping"]
    assert clip["dtype"] == "float64"
    assert clip["applied_identically_to_both_classifiers"] is True
    assert 0.0 < float(clip["epsilon"]) < 1.0


def test_h2_prose_and_config_agree_on_target_and_sign() -> None:
    for rel in (
        "preregistration/amendment-v0.1.2.md",
        "preregistration/analysis-plan.md",
        "preregistration/hypotheses.md",
    ):
        text = (REPO / rel).read_text(encoding="utf-8")
        assert "log_loss_prompt_embedding - log_loss_hidden_state" in text, rel
        for label in STRATEGY_SUPERCLASSES:
            assert label in text, (rel, label)
        assert "log_loss_hidden_state - log_loss_prompt_embedding" not in text, rel


# --------------------------------------------------------------------------- #
# Probe pipeline, regularization grid, tie-breaking
# --------------------------------------------------------------------------- #
def test_probe_pipeline_and_c_grid_are_frozen() -> None:
    pipeline = _pilot()["analysis"]["probe_pipeline"]
    assert pipeline["penalty"] == "l2"
    assert pipeline["solver"] == "lbfgs"
    assert pipeline["scaler_fit_scope"] == "relevant_training_subset_only"
    assert "StandardScaler" in pipeline["scaler"]
    assert pipeline["fit_intercept"] is True
    assert pipeline["class_weight"] is None
    assert pipeline["max_iter"] == 5000
    assert float(pipeline["tol"]) == 1e-6
    assert pipeline["dtype"] == "float64"
    assert tuple(float(c) for c in pipeline["regularization_grid_C"]) == (
        REGULARIZATION_C_GRID
    )
    assert REGULARIZATION_C_GRID == (1e-4, 1e-3, 1e-2, 1e-1, 1.0, 10.0, 100.0)
    assert pipeline["sparse_baselines_are_secondary"] is True


@pytest.mark.parametrize(
    "key,value",
    [
        ("solver", "liblinear"),
        ("penalty", "l1"),
        ("scaler_fit_scope", "all_data"),
        ("regularization_grid_C", [1.0]),
    ],
)
def test_altered_pipeline_or_grid_is_rejected(key: str, value: object) -> None:
    data = _pilot()
    data["analysis"]["probe_pipeline"][key] = value
    with pytest.raises(ValidationError):
        validate_statistical_specification(data)


def test_missing_scaler_is_rejected() -> None:
    data = _pilot()
    del data["analysis"]["probe_pipeline"]["scaler"]
    with pytest.raises(ValidationError):
        validate_statistical_specification(data)


def test_selection_objectives_and_tie_breaking_are_declared() -> None:
    selection = _pilot()["analysis"]["hyperparameter_selection"]
    assert selection["h1_inner_objective"] == (
        "highest_pooled_inner_validation_balanced_accuracy"
    )
    assert selection["h2_inner_objective"] == (
        "lowest_pooled_inner_validation_response_strategy_log_loss"
    )
    assert selection["first_tie_break"] == "smaller_C_stronger_regularization"
    assert selection["second_tie_break_hidden_state"] == "earlier_layer_index"
    assert 0.0 < float(selection["numerical_tie_tolerance"]) < 1.0
    assert selection["selection_scope"] == "outer_training_domains_only"


def test_missing_tie_breaking_is_rejected() -> None:
    data = _pilot()
    del data["analysis"]["hyperparameter_selection"]["numerical_tie_tolerance"]
    with pytest.raises(ValidationError):
        validate_statistical_specification(data)


# --------------------------------------------------------------------------- #
# Seed roles
# --------------------------------------------------------------------------- #
def test_seed_roles_are_frozen_and_never_pooled() -> None:
    analysis = _pilot()["analysis"]
    assert analysis["primary_seed"] == PRIMARY_SEED == 0
    assert tuple(analysis["sensitivity_seeds"]) == SENSITIVITY_SEEDS == (1, 2, 3, 4)
    assert analysis["bootstrap_seed"] == BOOTSTRAP_SEED == 20260830
    assert analysis["permutation_seed"] == PERMUTATION_SEED == 20260831
    assert analysis["pool_predictions_across_seeds"] is False
    assert analysis["primary_decision_uses_primary_seed_only"] is True
    assert analysis["split_assignments_depend_on_seed"] is False


def test_pooling_predictions_across_seeds_is_rejected() -> None:
    data = _pilot()
    data["analysis"]["pool_predictions_across_seeds"] = True
    with pytest.raises(ValidationError):
        validate_statistical_specification(data)


def test_no_stale_example_five_seed_language_remains() -> None:
    stale = re.compile(r"preregistered count,\s*e\.g\.\s*5", re.IGNORECASE)
    for path in sorted(REPO.glob("preregistration/*.md")):
        assert not stale.search(path.read_text(encoding="utf-8")), path.name
    assert not stale.search((REPO / "paper/main.tex").read_text(encoding="utf-8"))


# --------------------------------------------------------------------------- #
# Inner leave-one-training-domain-out selection
# --------------------------------------------------------------------------- #
def test_inner_folds_are_leave_one_training_domain_out() -> None:
    items = _stimuli()
    outer = plan_double_crossed_lodo(items)[0]
    inner = plan_inner_selection_folds(items, outer)
    assert len(inner) == INNER_LODO_FOLDS == 3
    by_id = {item.item_id: item for item in items}
    seen_validation_domains = set()
    for fold in inner:
        assert len(fold.inner_training_domains) == 2
        assert fold.inner_validation_domain not in fold.inner_training_domains
        assert fold.outer_test_domain not in fold.inner_training_domains
        assert fold.inner_validation_domain != fold.outer_test_domain
        seen_validation_domains.add(fold.inner_validation_domain)
        # every validation item comes from exactly the inner validation domain
        assert {by_id[i].domain for i in fold.validation_item_ids} == {
            fold.inner_validation_domain
        }
        # every training item comes from exactly the two inner fit domains
        assert {by_id[i].domain for i in fold.training_item_ids} == set(
            fold.inner_training_domains
        )
    assert seen_validation_domains == set(DOMAINS) - {outer.test_domain}


def test_inner_folds_never_mix_domains_within_a_validation_side() -> None:
    items = _stimuli()
    by_id = {item.item_id: item for item in items}
    for outer in plan_double_crossed_lodo(items):
        for fold in plan_inner_selection_folds(items, outer):
            domains = {by_id[i].domain for i in fold.validation_item_ids}
            assert len(domains) == 1, "inner validation fold mixed domains"


def test_outer_test_domain_never_enters_inner_selection() -> None:
    items = _stimuli()
    by_id = {item.item_id: item for item in items}
    for outer in plan_double_crossed_lodo(items):
        for fold in plan_inner_selection_folds(items, outer):
            selected = fold.training_item_ids + fold.validation_item_ids
            assert all(by_id[i].domain != outer.test_domain for i in selected)
            selected_groups = set(fold.training_group_ids) | set(
                fold.validation_group_ids
            )
            assert selected_groups.isdisjoint(outer.test_group_ids)


def test_inner_direction_stays_crossed() -> None:
    items = _stimuli()
    by_id = {item.item_id: item for item in items}
    outer = next(
        f
        for f in plan_double_crossed_lodo(items)
        if f.direction == CONCEPT_ABSENT_TO_PRESENT
    )
    for fold in plan_inner_selection_folds(items, outer):
        assert {by_id[i].cell for i in fold.training_item_ids} == {
            "A_neutral_control",
            "C_pure_task_induction",
        }
        assert {by_id[i].cell for i in fold.validation_item_ids} == {
            "B_concept_tracking_only",
            "D_combined",
        }


def test_no_matched_group_crosses_any_boundary() -> None:
    items = _stimuli()
    for outer in plan_double_crossed_lodo(items):
        assert set(outer.training_group_ids).isdisjoint(outer.test_group_ids)
        for fold in plan_inner_selection_folds(items, outer):
            assert set(fold.training_group_ids).isdisjoint(fold.validation_group_ids)
            assert set(fold.training_item_ids).isdisjoint(fold.validation_item_ids)


def test_config_requires_leave_one_training_domain_out() -> None:
    inner = _pilot()["analysis"]["inner_validation"]
    assert inner["scheme"] == "leave_one_training_domain_out"
    assert inner["folds"] == 3
    assert inner["outer_test_domain_excluded"] is True
    data = _pilot()
    data["analysis"]["inner_validation"]["scheme"] = "round_robin_matched_groups"
    with pytest.raises(ValidationError):
        validate_statistical_specification(data)


# --------------------------------------------------------------------------- #
# Cluster bootstrap
# --------------------------------------------------------------------------- #
def test_bootstrap_resamples_complete_groups_not_items() -> None:
    items = _stimuli(groups_per_domain=3)
    plans = plan_cluster_bootstrap(items, resamples=25)
    assert len(plans) == 25
    all_group_ids = {item.matched_group_id for item in items}
    item_ids = {item.item_id for item in items}
    for plan in plans:
        assert set(plan.drawn_group_ids) <= all_group_ids
        assert not (set(plan.drawn_group_ids) & item_ids)
        assert len(plan.drawn_group_ids) == len(all_group_ids)


def test_bootstrap_preserves_domain_strata() -> None:
    items = _stimuli(groups_per_domain=3)
    strata = dict(held_out_groups_by_domain(items))
    domain_of = {item.matched_group_id: item.domain for item in items}
    for plan in plan_cluster_bootstrap(items, resamples=25):
        counts: dict[str, int] = {}
        for gid in plan.drawn_group_ids:
            counts[domain_of[gid]] = counts.get(domain_of[gid], 0) + 1
        assert counts == {d: len(g) for d, g in strata.items()}


def test_bootstrap_plan_is_deterministic_under_the_frozen_seed() -> None:
    items = _stimuli()
    a = plan_cluster_bootstrap(items, resamples=10)
    b = plan_cluster_bootstrap(items, resamples=10)
    assert [p.drawn_group_ids for p in a] == [p.drawn_group_ids for p in b]
    c = plan_cluster_bootstrap(items, resamples=10, seed=BOOTSTRAP_SEED + 1)
    assert [p.drawn_group_ids for p in a] != [p.drawn_group_ids for p in c]


def test_bootstrap_config_is_group_clustered_and_domain_stratified() -> None:
    bootstrap = _pilot()["analysis"]["bootstrap"]
    assert bootstrap["resamples"] == BOOTSTRAP_RESAMPLES == 1000
    assert bootstrap["resampling_unit"] == "complete_matched_group_cluster"
    assert bootstrap["stratified_within_held_out_domain"] is True
    assert bootstrap["preserves_groups_contributed_per_domain"] is True
    assert bootstrap["group_predictions_travel_together"] is True
    assert bootstrap["h1_predictions_per_held_out_group"] == 4
    assert bootstrap["h2_pairs_resampled_together"] is True
    assert [float(x) for x in bootstrap["interval_percentiles"]] == [2.5, 97.5]
    assert bootstrap["interval_type"] == "percentile"
    for flag in (
        "resample_items",
        "resample_cells",
        "resample_directions",
        "resample_seeds",
    ):
        assert bootstrap[flag] is False


@pytest.mark.parametrize(
    "key,value",
    [
        ("resampling_unit", "individual_item"),
        ("stratified_within_held_out_domain", False),
        ("resample_items", True),
    ],
)
def test_item_level_or_unstratified_bootstrap_is_rejected(
    key: str, value: object
) -> None:
    data = _pilot()
    data["analysis"]["bootstrap"][key] = value
    with pytest.raises(ValidationError):
        validate_statistical_specification(data)


# --------------------------------------------------------------------------- #
# Operational Benjamini-Hochberg
# --------------------------------------------------------------------------- #
def test_bh_declares_q_and_raw_p_value_procedures() -> None:
    fdr = _pilot()["fdr_families"]
    procedure = fdr["procedure"]
    assert float(procedure["q"]) == BH_Q == 0.05
    assert procedure["method"] == "benjamini_hochberg"
    assert procedure["operates_on"] == "preregistered_one_sided_raw_p_values"
    assert procedure["confidence_intervals_are_fdr_corrected"] is False
    assert procedure["secondary_can_replace_primary"] is False
    for family in ("h1_direction_domain_secondary", "h2_direction_domain_secondary"):
        raw = fdr[family]["raw_p_value_procedure"]
        assert raw["permutations"] == PERMUTATION_REPLICATES == 10000
        assert raw["plus_one_correction"] is True
        assert raw["seed"] == PERMUTATION_SEED
        assert raw["null_unit"] == "matched_group"
        assert raw["one_sided_direction"]


def test_missing_bh_q_or_raw_p_procedure_is_rejected() -> None:
    data = _pilot()
    del data["fdr_families"]["procedure"]["q"]
    with pytest.raises(ValidationError):
        validate_statistical_specification(data)

    data = _pilot()
    del data["fdr_families"]["h1_direction_domain_secondary"]["raw_p_value_procedure"]
    with pytest.raises(ValidationError):
        validate_statistical_specification(data)


def test_no_document_claims_an_fdr_corrected_confidence_interval() -> None:
    banned = re.compile(
        r"(FDR[- ]corrected\s+(?:confidence\s+)?(?:interval|CI)"
        r"|(?:confidence\s+interval|CI)\s+(?:is|are|has been|have been)\s+FDR)",
        re.IGNORECASE,
    )
    targets = sorted(REPO.glob("preregistration/*.md"))
    targets += [REPO / "README.md", REPO / "CHANGELOG.md", REPO / "paper/main.tex"]
    for path in targets:
        text = path.read_text(encoding="utf-8")
        assert not banned.search(text), f"{path.name} claims an FDR-corrected interval"


def test_family_and_h3_grids_remain_blocked() -> None:
    fdr = _pilot()["fdr_families"]
    assert str(fdr["h1_layer_position_sensitivity"]["status"]).startswith("TO_BE_")
    assert str(fdr["h3_intervention"]["status"]).startswith("TO_BE_")
    assert str(fdr["h3_intervention"]["raw_p_value_procedure"]).startswith("TO_BE_")
    assert str(fdr["family_structure_primary"]["raw_p_value_procedure"]).startswith(
        "TO_BE_"
    )


# --------------------------------------------------------------------------- #
# Manifest and run-readiness guards
# --------------------------------------------------------------------------- #
_HEX40_A = "a" * 40
_HEX40_B = "b" * 40
_HEX40_C = "c" * 40
_HEX40_D = "d" * 40
_SHA256 = "sha256:" + "e" * 64


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
        "model_revision": _HEX40_A,
        "tokenizer_revision": _HEX40_B,
        "prompt_embedding_model": "BAAI/bge-base-en-v1.5",
        "prompt_embedding_revision": _HEX40_C,
        "prompt_embedding_license": "mit",
        "prompt_embedding_pooling_rule": "cls_then_l2_normalize",
        "prompt_embedding_truncation_rule": "truncate_to_model_max_length",
        "prompt_embedding_max_input_length": 512,
        "chat_template": "qwen-chatml",
        "chat_template_hash": "sha256:" + "f" * 64,
        "code_commit": _HEX40_D,
        "seed": 0,
        "decoding": {"temperature": 0.0},
        "layer": 16,
        "token_position": "prompt_final_non_padding",
        "stimulus_file_hash": _SHA256,
        "output_directory": "experiments/results/ASCR-Mini-0/",
        "environment": "test-only",
        "timestamp": "2026-08-30T00:00:00Z",
    }
    data.update(overrides)
    return RunManifest(**data)  # type: ignore[arg-type]


def test_manifest_compat_fields_have_no_duplicates() -> None:
    assert len(_MANIFEST_COMPAT_FIELDS) == len(set(_MANIFEST_COMPAT_FIELDS))
    assert _MANIFEST_COMPAT_FIELDS.count("run_kind") == 1


def test_experiment_id_and_stimulus_hash_are_compatibility_fields() -> None:
    assert "experiment_id" in _MANIFEST_COMPAT_FIELDS
    assert "stimulus_file_hash" in _MANIFEST_COMPAT_FIELDS
    base = _manifest()
    other_hash = _manifest(stimulus_file_hash="sha256:" + "f" * 64)
    assert not manifests_compatible(base, other_hash)
    other_experiment = _manifest(experiment_id="ASCR-other")
    assert not manifests_compatible(base, other_experiment)


def test_intentional_compatibility_exclusions_are_preserved() -> None:
    for name in _MANIFEST_EXCLUDED_COMPAT_FIELDS:
        assert name not in _MANIFEST_COMPAT_FIELDS
    base = _manifest()
    varied = _manifest(
        shard_id="ASCR-Mini-1",
        seed=3,
        output_directory="experiments/results/ASCR-Mini-1/",
        timestamp="2026-09-01T00:00:00Z",
    )
    assert manifests_compatible(base, varied)


@pytest.mark.parametrize(
    "field",
    [
        "model_revision",
        "tokenizer_revision",
        "prompt_embedding_revision",
        "code_commit",
    ],
)
def test_scientific_manifest_rejects_nonimmutable_revision(field: str) -> None:
    for bad in ("abc1234", "main", "v1.0", _HEX40_A.upper(), _HEX40_A[:-1]):
        with pytest.raises(ValidationError):
            _manifest(**{field: bad}).validate(require_frozen_revision=True)
    _manifest().validate(require_frozen_revision=True)


def test_stimulus_file_hash_format_is_validated() -> None:
    for bad in ("sha256:abc", "abc", "sha1:" + "a" * 40, "sha256:" + "G" * 64):
        with pytest.raises(ValidationError):
            _manifest(stimulus_file_hash=bad).validate()
    _manifest().validate()


def test_smoke_manifest_may_declare_prompt_embedding_not_applicable() -> None:
    smoke = _manifest(
        shard_id="ASCR-Technical-Smoke-0",
        run_kind="technical_smoke",
        eligible_for_scientific_analysis=False,
        prompt_set_id="DISPOSABLE_TOKENIZER_SMOKE",
        prompt_set_version="smoke-v1",
        prompt_embedding_model=NOT_APPLICABLE_TECHNICAL_SMOKE,
        prompt_embedding_revision=NOT_APPLICABLE_TECHNICAL_SMOKE,
        prompt_embedding_license=NOT_APPLICABLE_TECHNICAL_SMOKE,
        prompt_embedding_pooling_rule=NOT_APPLICABLE_TECHNICAL_SMOKE,
        prompt_embedding_truncation_rule=NOT_APPLICABLE_TECHNICAL_SMOKE,
        prompt_embedding_max_input_length=0,
        output_directory="experiments/results/technical-smoke/run-0/",
    )
    smoke.validate(require_frozen_revision=True)
    assert not manifests_compatible(_manifest(), smoke)


def test_scientific_manifest_rejects_the_not_applicable_sentinel() -> None:
    with pytest.raises(ValidationError):
        _manifest(prompt_embedding_model=NOT_APPLICABLE_TECHNICAL_SMOKE).validate()
    with pytest.raises(ValidationError):
        _manifest(prompt_embedding_revision=NOT_APPLICABLE_TECHNICAL_SMOKE).validate()


def test_integrated_pre_run_gate_blocks_and_names_both_sources() -> None:
    config = load_config(PILOT)
    items = _stimuli()
    problems = integrated_pre_run_gate_problems(config, items)
    assert problems
    assert any(p.startswith("config:") for p in problems)
    assert any(p.startswith("stimuli:") for p in problems)
    assert not scientific_run_authorized(config, items)


# --------------------------------------------------------------------------- #
# Canonical release build
# --------------------------------------------------------------------------- #
def test_canonical_build_cannot_silently_switch_engines() -> None:
    makefile = (REPO / "Makefile").read_text(encoding="utf-8")
    assert "ASCR_CANONICAL_ENGINE ?= tectonic" in makefile
    assert "ASCR_CANONICAL_ENGINE_VERSION ?= 0.16.9" in makefile
    assert "paper paper-release:" in makefile
    assert "deterministic-mode" in makefile
    # The canonical recipe must not contain any latexmk fallback.
    start = makefile.index("paper paper-release:")
    end = makefile.index("paper-verify:")
    canonical_recipe = makefile[start:end]
    assert "latexmk" not in canonical_recipe
    assert "canonical engine version mismatch" in canonical_recipe
    assert "not found" in canonical_recipe
    # latexmk survives only as an explicitly noncanonical development target.
    dev = makefile[makefile.index("paper-dev:") :]
    assert "NONCANONICAL" in dev
    assert "-jobname=main-dev" in dev


def test_documented_canonical_engine_is_consistent() -> None:
    for rel in (
        "README.md",
        "preregistration/amendment-v0.1.2.md",
        "preregistration/v0.1.2-review-status.md",
    ):
        text = (REPO / rel).read_text(encoding="utf-8")
        assert "Tectonic 0.16.9" in text, rel


# --------------------------------------------------------------------------- #
# Publication status and no-data guards
# --------------------------------------------------------------------------- #
def test_v012_is_declared_released_with_assigned_zenodo_doi() -> None:
    release_claim = re.compile(
        r"v0\.1\.2[\s\S]{0,120}?\b(?:(?:is|was)\s+)?"
        r"(?:released|published|tagged|merged)\b",
        re.IGNORECASE,
    )
    # Guard both the original grammatical form and the README form that escaped it.
    assert release_claim.search("v0.1.2 is released")
    assert release_claim.search("v0.1.2: GitHub Release published")

    targets = (
        REPO / "README.md",
        REPO / "CHANGELOG.md",
        REPO / "preregistration/amendment-v0.1.2.md",
        REPO / "preregistration/v0.1.2-review-status.md",
        REPO / "paper/main.tex",
    )
    # The paper source/PDF are retained archival artifacts, not current metadata;
    # their pre-assignment DOI wording is documented in the README/review status.
    stale_status = re.compile(
        r"v0\.1\.2[\s\S]{0,160}?\b(?:unreleased|not\s+(?:yet\s+)?"
        r"(?:merged|tagged|released|archived))\b",
        re.IGNORECASE,
    )
    forbidden_pdf_status = re.compile(
        r"(?:paper/preprint\.pdf|(?:committed|release)\s+PDF)"
        r"[\s\S]{0,160}?\b(?:local review artifact|review artifact only|"
        r"must not be attached|must not be deposited)\b",
        re.IGNORECASE,
    )
    stale_doi_status = re.compile(
        r"(?:Zenodo\s+DOI|DOI\s+assignment|version-specific\s+(?:Zenodo\s+)?DOI)"
        r"\s+(?:(?:is|remains)\s+)?pending",
        re.IGNORECASE,
    )
    assert stale_doi_status.search("version-specific Zenodo DOI pending")
    assert stale_doi_status.search("Zenodo DOI is\npending")
    for path in targets:
        text = path.read_text(encoding="utf-8")
        assert release_claim.search(text), path.name
        if path != REPO / "paper/main.tex":
            assert "10.5281/zenodo.22232409" in text, path.name
            assert not stale_doi_status.search(text), path.name
        assert not stale_status.search(text), path.name
        assert not forbidden_pdf_status.search(text), path.name
    cff = yaml.safe_load((REPO / "CITATION.cff").read_text(encoding="utf-8"))
    assert str(cff["date-released"]) == "2026-08-31"
    assert cff["doi"] == "10.5281/zenodo.22232409"
    assert cff["preferred-citation"]["doi"] == cff["doi"]


def test_branch_is_not_declared_run_ready() -> None:
    config = load_config(PILOT)
    assert config.validation_mode == "draft"
    assert not ascr.config_can_generate_scientific_data(config)
    mini0 = yaml.safe_load(MINI0.read_text(encoding="utf-8"))
    assert mini0["status"] == "PRE_DATA_UNFROZEN"
    assert str(mini0["model_revision"]).startswith("TO_BE_")


def test_remaining_author_decisions_are_listed_everywhere() -> None:
    mini0_expected = {
        "prompt_embedding_selection_and_immutable_details",
        "qwen_model_revision",
        "tokenizer_revision",
        "primary_layer_candidate_grid",
        "exact_position_sensitivity_grid",
    }
    assert (
        set(_pilot()["run_gate"]["remaining_mini0_author_decisions"]) == mini0_expected
    )
    assert _pilot()["run_gate"]["deferred_non_mini0_author_decisions"] == [
        "later_h3_intervention_grid"
    ]
    mini0 = yaml.safe_load(MINI0.read_text(encoding="utf-8"))
    assert set(mini0["remaining_mini0_author_decisions"]) == mini0_expected
    assert mini0["deferred_non_mini0_author_decisions"] == [
        "later_h3_intervention_grid"
    ]


def test_no_data_or_result_artifacts_exist() -> None:
    for sub in ("experiments/data", "experiments/results"):
        stray = [
            p.name
            for p in (REPO / sub).iterdir()
            if p.is_file() and p.name != "README.md"
        ]
        assert stray == [], f"unexpected files in {sub}: {stray}"
    assert not list((REPO / "paper/figures").glob("*.png"))
    assert not list((REPO / "paper/figures").glob("*.pdf"))


def test_historical_v011_config_is_exempt_from_the_v012_specification() -> None:
    cfg = parse_config(
        {
            "config_version": "0.1.1",
            "model": {
                "name": "Qwen/Qwen2.5-7B-Instruct",
                "revision": "historical-sha",
            },
            "design": {"axes": ["uncertainty"], "domains": list(ascr.DOMAINS)},
            "activations": {"layers": "all"},
            "analysis": {"seeds": [0]},
        }
    )
    assert cfg.is_historical
