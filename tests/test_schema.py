"""Tests for the ASCR prompt-item schema and config validation."""

from __future__ import annotations

import pytest
from ascr import schema
from ascr.schema import (
    PLACEHOLDER_MODEL_REVISION,
    PLACEHOLDER_REPLICATION_MODEL,
    PromptItem,
    RunManifest,
    ValidationError,
    is_complete_matched_group,
    is_placeholder_revision,
    item_from_dict,
    item_to_dict,
    manifests_compatible,
    parse_config,
    validate_matched_group,
)


def _base_item(**overrides: object) -> dict[str, object]:
    data: dict[str, object] = {
        "item_id": "unc-dbg-0001-C",
        "axis": "uncertainty",
        "domain": "software_debugging",
        "task_state_present": True,
        "concept_mention_present": False,
        "prompt_text": "Fix the function below.",
        "matched_group_id": "unc-dbg-0001",
        "expected_strategy_space": ["clarification_request", "abstention"],
        "notes": "pure task induction cell",
    }
    data.update(overrides)
    return data


def test_valid_item_round_trips_and_derives_cell() -> None:
    item = item_from_dict(_base_item())
    assert isinstance(item, PromptItem)
    assert item.cell == "C_pure_task_induction"


@pytest.mark.parametrize(
    "task_state,concept,expected",
    [
        (False, False, "A_neutral_control"),
        (False, True, "B_concept_tracking_only"),
        (True, False, "C_pure_task_induction"),
        (True, True, "D_combined"),
    ],
)
def test_cell_derivation(task_state: bool, concept: bool, expected: str) -> None:
    item = item_from_dict(
        _base_item(task_state_present=task_state, concept_mention_present=concept)
    )
    assert item.cell == expected


def test_missing_field_is_rejected() -> None:
    data = _base_item()
    del data["prompt_text"]
    with pytest.raises(ValidationError):
        item_from_dict(data)


def test_unknown_field_is_rejected() -> None:
    with pytest.raises(ValidationError):
        item_from_dict(_base_item(bogus="x"))


def test_unknown_axis_is_rejected() -> None:
    with pytest.raises(ValidationError):
        item_from_dict(_base_item(axis="not_an_axis"))


def test_unknown_domain_is_rejected() -> None:
    with pytest.raises(ValidationError):
        item_from_dict(_base_item(domain="astrology"))


def test_empty_strategy_space_is_rejected() -> None:
    with pytest.raises(ValidationError):
        item_from_dict(_base_item(expected_strategy_space=[]))


def test_unknown_strategy_is_rejected() -> None:
    with pytest.raises(ValidationError):
        item_from_dict(_base_item(expected_strategy_space=["teleport"]))


def test_blank_item_id_is_rejected() -> None:
    with pytest.raises(ValidationError):
        item_from_dict(_base_item(item_id="   "))


def _full_group() -> list[PromptItem]:
    items = []
    for cell, (ts, cm) in {
        "A": (False, False),
        "B": (False, True),
        "C": (True, False),
        "D": (True, True),
    }.items():
        items.append(
            item_from_dict(
                _base_item(
                    item_id=f"unc-dbg-0001-{cell}",
                    task_state_present=ts,
                    concept_mention_present=cm,
                    expected_strategy_space=["direct_compliance", "abstention"],
                )
            )
        )
    return items


def test_complete_matched_group_validates() -> None:
    validate_matched_group(_full_group())


def test_matched_group_rejects_duplicate_cells() -> None:
    items = _full_group()
    dup = item_from_dict(
        _base_item(
            item_id="unc-dbg-0001-A2",
            task_state_present=False,
            concept_mention_present=False,
            expected_strategy_space=["direct_compliance"],
        )
    )
    with pytest.raises(ValidationError):
        validate_matched_group(items + [dup])


def test_matched_group_rejects_mixed_axis() -> None:
    items = _full_group()
    other = item_from_dict(
        _base_item(
            item_id="unc-dbg-0001-X",
            axis="norm_tension",
            task_state_present=True,
            concept_mention_present=False,
            matched_group_id="unc-dbg-0001",
            expected_strategy_space=["refusal"],
        )
    )
    # replace one sibling to keep cells unique but mix the axis
    with pytest.raises(ValidationError):
        validate_matched_group(items[:3] + [other])


# ---------------------------------------------------------------------------
# Config validation
# ---------------------------------------------------------------------------
def _base_config() -> dict[str, object]:
    return {
        "config_version": "0.1.2",
        "model": {
            "name": "Qwen/Qwen2.5-7B-Instruct",
            "revision": "TO_BE_FROZEN_BEFORE_DATA_GENERATION",
            "tokenizer_revision": "TO_BE_FROZEN_BEFORE_DATA_GENERATION",
            "replication_model": "TO_BE_SELECTED_BEFORE_CONFIRMATORY_REPLICATION",
        },
        "design": {
            "axes": ["uncertainty", "norm_tension", "controllability"],
            "domains": [
                "software_debugging",
                "scheduling_planning",
                "policy_constrained_assistance",
                "document_editing",
            ],
        },
        "activations": {"layers": "all"},
        "analysis": _frozen_analysis(),
        "fdr_families": _frozen_fdr_families(),
        "family_structure_test": dict(_pilot_yaml()["family_structure_test"]),
        "prompt_embedding": {
            "model_name": "TO_BE_SELECTED_BY_AUTHOR_BEFORE_MINI_0",
            "revision": "TO_BE_FROZEN_AFTER_AUTHOR_SELECTION",
            "selection_status": "AUTHOR_APPROVAL_REQUIRED",
        },
    }


def _frozen_analysis() -> dict[str, object]:
    """The frozen v0.1.2 analysis block, read from the committed pilot config.

    Reusing the real configuration keeps these tests from drifting away from the
    registered specification.
    """
    return dict(_pilot_yaml()["analysis"])


def _frozen_fdr_families() -> dict[str, object]:
    return dict(_pilot_yaml()["fdr_families"])


def _pilot_yaml() -> dict:
    import pathlib as _pathlib

    import yaml as _yaml

    root = _pathlib.Path(schema.__file__).resolve().parents[3]
    return _yaml.safe_load(
        (root / "experiments/configs/pilot.yaml").read_text(encoding="utf-8")
    )


def test_parse_config_ok() -> None:
    cfg = parse_config(_base_config())
    assert cfg.model_name == "Qwen/Qwen2.5-7B-Instruct"
    assert cfg.seeds == (0, 1, 2, 3, 4)
    assert "uncertainty" in cfg.axes


def test_parse_config_rejects_unknown_axis() -> None:
    data = _base_config()
    data["design"]["axes"] = ["uncertainty", "mystery_axis"]  # type: ignore[index]
    with pytest.raises(ValidationError):
        parse_config(data)


def test_parse_config_rejects_a_config_without_the_frozen_specification() -> None:
    data = _base_config()
    data["analysis"] = {"seeds": [0, 1, 2, 3, 4]}
    with pytest.raises(ValidationError):
        parse_config(data)


def test_parse_config_requires_seeds() -> None:
    data = _base_config()
    data["analysis"]["seeds"] = []  # type: ignore[index]
    with pytest.raises(ValidationError):
        parse_config(data)


def test_parse_config_requires_sections() -> None:
    with pytest.raises(ValidationError):
        parse_config(
            {"config_version": "0.1.2", "model": {"name": "x", "revision": "y"}}
        )


def test_parse_config_requires_config_version() -> None:
    data = _base_config()
    del data["config_version"]
    with pytest.raises(ValidationError):
        parse_config(data)


def test_parse_config_rejects_replication_equal_to_primary() -> None:
    data = _base_config()
    data["model"]["replication_model"] = data["model"]["name"]  # type: ignore[index]
    with pytest.raises(ValidationError):
        parse_config(data)


def test_parse_config_allows_placeholder_replication() -> None:
    cfg = parse_config(_base_config())
    assert cfg.replication_model == PLACEHOLDER_REPLICATION_MODEL
    assert not cfg.revision_is_frozen  # still a placeholder revision


def test_load_config_reads_pilot_yaml(tmp_path=None) -> None:
    # Load the committed pilot config from the repository to ensure it stays valid.
    import pathlib

    # schema.py -> ascr -> src -> experiments; configs/ lives under experiments/.
    pilot = (
        pathlib.Path(schema.__file__).resolve().parents[2] / "configs" / "pilot.yaml"
    )
    cfg = schema.load_config(pilot)
    assert cfg.model_name.startswith("Qwen/")
    assert cfg.seeds
    assert cfg.config_version == "0.1.2"
    # Replication model must not be the primary model (v0.1.1 amendment).
    assert cfg.replication_model != cfg.model_name


# ---------------------------------------------------------------------------
# v0.1.2: placeholder revisions, QA metadata, matched-group completeness,
# mini-shard/smoke manifests, and the no-results guard.
# ---------------------------------------------------------------------------
def test_placeholder_revision_detected() -> None:
    assert is_placeholder_revision(PLACEHOLDER_MODEL_REVISION)
    assert is_placeholder_revision(PLACEHOLDER_REPLICATION_MODEL)
    assert not is_placeholder_revision("a1b2c3d4e5f6")


def _qa_ok() -> dict[str, object]:
    """A complete, typed, run_ready-passing QA record."""
    from ascr.schema import QA_BOOLEAN_FIELDS

    qa: dict[str, object] = {name: True for name in QA_BOOLEAN_FIELDS}
    qa.update(
        naturalness_rating=5,
        observed_task_state_present=True,
        observed_concept_mention_present=False,
        non_target_axes_absent_confirmed={
            "norm_tension": True,
            "controllability": True,
        },
        reviewer_id="rev-1",
        review_timestamp="2026-07-12T10:00:00Z",
        disposition="pass",
    )
    return qa


def test_item_accepts_qa_block_in_draft_mode() -> None:
    # A partial QA block is allowed while authoring (draft mode).
    item = item_from_dict(_base_item(qa={"grammatical": True}))
    assert item.qa is not None


def test_item_accepts_complete_typed_qa_block() -> None:
    item = item_from_dict(_base_item(qa=_qa_ok()))
    assert item.qa is not None
    item.validate(mode="run_ready")  # complete typed QA passes strict validation


def test_item_serialization_preserves_v012_qa() -> None:
    item = item_from_dict(_base_item(qa=_qa_ok()))
    assert item_from_dict(item_to_dict(item)) == item


def test_complete_matched_group_helper() -> None:
    assert is_complete_matched_group(_full_group())
    # Drop one cell -> not complete.
    assert not is_complete_matched_group(_full_group()[:3])


def _manifest(**overrides: object) -> RunManifest:
    base: dict[str, object] = {
        "experiment_id": "ASCR-pilot",
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
        "token_position": "prompt_final",
        "stimulus_file_hash": "sha256:" + "e" * 64,
        "output_directory": "experiments/results/ASCR-Mini-0/",
        "environment": "py3.11-linux",
        "timestamp": "2026-07-12T00:00:00Z",
    }
    base.update(overrides)
    return RunManifest(**base)  # type: ignore[arg-type]


def test_manifest_validates_and_requires_frozen_revision() -> None:
    m = _manifest()
    m.validate()  # ok with a real revision
    m.validate(require_frozen_revision=True)  # still ok

    placeholder = _manifest(model_revision=PLACEHOLDER_MODEL_REVISION)
    placeholder.validate()  # allowed when not requiring frozen
    with pytest.raises(ValidationError):
        placeholder.validate(require_frozen_revision=True)


def test_manifests_compatible_only_when_relevant_fields_match() -> None:
    a = _manifest()
    # Different shard id / seed / output directory / timestamp are still combinable.
    b = _manifest(
        shard_id="ASCR-Mini-1",
        seed=3,
        output_directory="experiments/results/ASCR-Mini-1/",
        timestamp="2026-07-12T01:00:00Z",
    )
    assert manifests_compatible(a, b)
    # A different stimulus file is NOT combinable (v0.1.2 correction).
    stimulus = _manifest(stimulus_file_hash="sha256:" + "f" * 64)
    assert not manifests_compatible(a, stimulus)
    # A different experiment is NOT combinable (v0.1.2 correction).
    experiment = _manifest(experiment_id="ASCR-other")
    assert not manifests_compatible(a, experiment)
    # Different model revision breaks compatibility.
    c = _manifest(model_revision="0" * 40)
    assert not manifests_compatible(a, c)
    # Different decoding config breaks compatibility.
    d = _manifest(decoding={"temperature": 0.7})
    assert not manifests_compatible(a, d)


def test_no_result_files_are_committed() -> None:
    # Guard: experiments/data and experiments/results must contain only READMEs,
    # so fabricated results are never published as real ones.
    import pathlib

    root = pathlib.Path(schema.__file__).resolve().parents[3]
    for sub in ("experiments/data", "experiments/results"):
        d = root / sub
        stray = [p.name for p in d.iterdir() if p.is_file() and p.name != "README.md"]
        assert stray == [], f"unexpected non-README files in {sub}: {stray}"
