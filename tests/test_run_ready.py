"""Tests for the v0.1.2 run-ready gate: typed QA, matched-group QA,
external provenance, the config gate, and status/metadata consistency.

No model is run; these validate the pre-data enforcement machinery only.
"""

from __future__ import annotations

import pathlib

import pytest
import yaml
from ascr import schema
from ascr.schema import (
    PLACEHOLDER_MODEL_REVISION,
    QA_BOOLEAN_FIELDS,
    ValidationError,
    check_run_ready,
    is_run_ready,
    item_from_dict,
    provenance_is_run_ready,
    qa_item_passes,
    validate_qa,
    validate_run_ready_group,
)

REPO = pathlib.Path(schema.__file__).resolve().parents[3]


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
def _qa(
    naturalness: int = 5,
    *,
    task_state: bool = True,
    concept_mention: bool = False,
    axis: str = "uncertainty",
    **overrides: object,
) -> dict[str, object]:
    qa: dict[str, object] = {name: True for name in QA_BOOLEAN_FIELDS}
    qa.update(
        naturalness_rating=naturalness,
        observed_task_state_present=task_state,
        observed_concept_mention_present=concept_mention,
        non_target_axes_absent_confirmed={
            name: True
            for name in ("uncertainty", "norm_tension", "controllability")
            if name != axis
        },
        reviewer_id="rev-1",
        review_timestamp="2026-07-12T10:00:00Z",
        disposition="pass",
    )
    qa.update(overrides)
    return qa


def _item(
    cell_flags: tuple[bool, bool],
    *,
    qa: dict[str, object] | None,
    gid: str = "unc-dbg-0001",
    provenance: dict[str, object] | None = None,
):
    ts, cm = cell_flags
    data: dict[str, object] = {
        "item_id": f"{gid}-{int(ts)}{int(cm)}",
        "axis": "uncertainty",
        "domain": "software_debugging",
        "task_state_present": ts,
        "concept_mention_present": cm,
        "prompt_text": "Fix the function below.",
        "matched_group_id": gid,
        "expected_strategy_space": ["abstention", "clarification_request"],
    }
    if qa is not None:
        data["qa"] = qa
    if provenance is not None:
        data["provenance"] = provenance
    return item_from_dict(data)


def _full_group(naturals: tuple[int, int, int, int] = (5, 5, 4, 5)):
    cells = [(False, False), (False, True), (True, False), (True, True)]
    return [
        _item(
            c,
            qa=_qa(
                naturalness=n,
                task_state=c[0],
                concept_mention=c[1],
            ),
        )
        for c, n in zip(cells, naturals)
    ]


# --------------------------------------------------------------------------- #
# Typed run_ready QA
# --------------------------------------------------------------------------- #
def test_draft_allows_partial_qa_but_run_ready_rejects_it() -> None:
    partial = {"grammatical": True}
    validate_qa(partial, mode="draft")  # ok
    with pytest.raises(ValidationError):
        validate_qa(partial, mode="run_ready")


def test_run_ready_qa_rejects_wrong_types() -> None:
    bad = _qa()
    bad["grammatical"] = "yes"  # not a bool
    with pytest.raises(ValidationError):
        validate_qa(bad, mode="run_ready")


def test_naturalness_must_be_int_1_to_5() -> None:
    with pytest.raises(ValidationError):
        validate_qa(_qa(naturalness=6), mode="run_ready")
    with pytest.raises(ValidationError):
        validate_qa({**_qa(), "naturalness_rating": True}, mode="run_ready")


def test_qa_item_passes_requires_pass_flags_and_naturalness() -> None:
    assert qa_item_passes(_qa())
    assert not qa_item_passes(_qa(naturalness=3))  # below threshold
    assert not qa_item_passes(_qa(disposition="revise"))
    assert not qa_item_passes(_qa(disposition="discard"))
    assert not qa_item_passes(_qa(primary_axis_isolated=False))  # axis isolation


def test_missing_axis_isolation_flag_fails_item_run_ready() -> None:
    item = _item(
        (True, False),
        qa=_qa(task_state=True, concept_mention=False, primary_axis_isolated=False),
    )
    with pytest.raises(ValidationError):
        item.validate(mode="run_ready")


# --------------------------------------------------------------------------- #
# Matched-group run_ready + naturalness spread
# --------------------------------------------------------------------------- #
def test_complete_group_is_run_ready() -> None:
    validate_run_ready_group(_full_group())
    assert is_run_ready(_full_group())


def test_group_naturalness_spread_over_one_point_fails() -> None:
    with pytest.raises(ValidationError):
        validate_run_ready_group(_full_group(naturals=(5, 5, 3, 5)))


def test_incomplete_group_fails_run_ready() -> None:
    with pytest.raises(ValidationError):
        validate_run_ready_group(_full_group()[:3])


# --------------------------------------------------------------------------- #
# Whole-set gate: revision, sample size, external provenance
# --------------------------------------------------------------------------- #
def test_placeholder_revision_blocks_run() -> None:
    problems = check_run_ready(_full_group(), model_revision=PLACEHOLDER_MODEL_REVISION)
    assert any("placeholder" in p for p in problems)
    assert check_run_ready(_full_group(), model_revision="a" * 40) == []
    assert check_run_ready(_full_group(), model_revision="deadbeef")


def test_missing_sample_size_blocks_run() -> None:
    problems = check_run_ready(_full_group(), min_complete_groups=40)
    assert any("sample-size" in p for p in problems)


def _provenance(
    decision: str = "include", reviewed: str = "unanswerable"
) -> dict[str, object]:
    return {
        "dataset_name": "ExampleQA",
        "version": "1.0",
        "split": "dev",
        "original_id": "q42",
        "license": "CC-BY-4.0",
        "source": "https://example.org",
        "retrieval_date": "2026-07-12",
        "original_label": "unanswerable",
        "human_reviewed_label": reviewed,
        "reviewer_id": "rev-1",
        "adjustments": "none",
        "contamination_risk": "unknown",
        "decision": decision,
    }


def test_external_item_without_review_blocks_run() -> None:
    assert provenance_is_run_ready(_provenance())
    assert not provenance_is_run_ready(_provenance(decision="exclude"))
    assert not provenance_is_run_ready(_provenance(reviewed="  "))

    group = _full_group()
    # attach an unreviewed provenance to one item
    flagged = _item(
        (True, True),
        qa=_qa(task_state=True, concept_mention=True),
        provenance=_provenance(decision="revise"),
    )
    problems = check_run_ready(group[:3] + [flagged])
    assert any("provenance" in p for p in problems)


# --------------------------------------------------------------------------- #
# Config gate: holonomy exclusion + temperature-0/seed policy
# --------------------------------------------------------------------------- #
def _pilot() -> dict:
    return yaml.safe_load((REPO / "experiments/configs/pilot.yaml").read_text())


def test_config_has_no_holonomy_flag_for_all_shards() -> None:
    cfg = _pilot()
    assert cfg["no_holonomy_data"] is True
    for shard in cfg["mini_shards"]:
        # every ASCR shard must not collect holonomy data
        assert shard.get("no_holonomy_data", True) is True
        assert shard.get("kind") == "feasibility"


def test_config_temperature_zero_and_seed_policy() -> None:
    pol = _pilot()["temperature_zero_generation_policy"]
    assert pol["primary_temperature"] == 0.0
    assert pol["deterministic_single_generation"] is True
    assert pol["seeds_are_independent_text_samples"] is False


def test_config_no_arbitrary_family_margin() -> None:
    fam = _pilot()["family_structure_test"]
    assert fam["family_rank_grid"] == [1, 2]
    assert fam["arbitrary_margin"] == "none"
    assert set(fam["require_all_of"]) == {
        "A_shared_vs_separate",
        "B_behavioral_specificity",
        "C_incremental",
    }


def test_config_replication_differs_from_primary() -> None:
    cfg = schema.load_config(REPO / "experiments/configs/pilot.yaml")
    assert cfg.replication_model != cfg.model_name


# --------------------------------------------------------------------------- #
# Status / metadata consistency (v0.1.2)
# --------------------------------------------------------------------------- #
def test_changed_docs_declare_v012_status() -> None:
    changed = [
        "preregistration/experimental-design.md",
        "preregistration/analysis-plan.md",
        "preregistration/controls-and-baselines.md",
        "preregistration/response-strategy-taxonomy.md",
    ]
    for rel in changed:
        head = (REPO / rel).read_text(encoding="utf-8")[:400]
        assert "v0.1.2 pre-data methodological correction" in head, rel
        assert "v0.1 preregistration draft" not in head, rel


def test_hypothesis_docs_identify_v012_rule_correction() -> None:
    for rel in (
        "preregistration/hypotheses.md",
        "preregistration/falsification-criteria.md",
    ):
        head = (REPO / rel).read_text(encoding="utf-8")[:400]
        assert "v0.1.2" in head, rel


def test_no_result_files_committed_under_experiments() -> None:
    for sub in ("experiments/data", "experiments/results"):
        stray = [
            p.name
            for p in (REPO / sub).iterdir()
            if p.is_file() and p.name != "README.md"
        ]
        assert stray == [], f"unexpected files in {sub}: {stray}"
