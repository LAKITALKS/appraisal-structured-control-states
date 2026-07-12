"""Tests for the ASCR prompt-item schema and config validation."""

from __future__ import annotations

import pytest

from ascr import schema
from ascr.schema import (
    PLACEHOLDER_MODEL_REVISION,
    PLACEHOLDER_REPLICATION_MODEL,
    REQUIRED_QA_FIELDS,
    PromptItem,
    RunManifest,
    ValidationError,
    is_complete_matched_group,
    is_placeholder_revision,
    item_from_dict,
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
        "config_version": "0.1.1",
        "model": {
            "name": "Qwen/Qwen2.5-7B-Instruct",
            "revision": "TO_BE_FROZEN_BEFORE_DATA_GENERATION",
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
        "analysis": {"seeds": [0, 1, 2, 3, 4]},
    }


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


def test_parse_config_requires_seeds() -> None:
    data = _base_config()
    data["analysis"]["seeds"] = []  # type: ignore[index]
    with pytest.raises(ValidationError):
        parse_config(data)


def test_parse_config_requires_sections() -> None:
    with pytest.raises(ValidationError):
        parse_config({"config_version": "0.1.1", "model": {"name": "x", "revision": "y"}})


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
        pathlib.Path(schema.__file__).resolve().parents[2]
        / "configs"
        / "pilot.yaml"
    )
    cfg = schema.load_config(pilot)
    assert cfg.model_name.startswith("Qwen/")
    assert cfg.seeds
    assert cfg.config_version == "0.1.1"
    # Replication model must not be the primary model (v0.1.1 amendment).
    assert cfg.replication_model != cfg.model_name


# ---------------------------------------------------------------------------
# v0.1.1 amendment: placeholder revision, QA metadata, matched-group completeness,
# mini-shard manifests, and the no-results guard.
# ---------------------------------------------------------------------------
def test_placeholder_revision_detected() -> None:
    assert is_placeholder_revision(PLACEHOLDER_MODEL_REVISION)
    assert is_placeholder_revision(PLACEHOLDER_REPLICATION_MODEL)
    assert not is_placeholder_revision("a1b2c3d4e5f6")


def _qa_ok() -> dict[str, object]:
    return {k: True for k in REQUIRED_QA_FIELDS}


def test_item_accepts_complete_qa_block() -> None:
    item = item_from_dict(_base_item(qa=_qa_ok()))
    assert item.qa is not None


def test_item_rejects_incomplete_qa_block() -> None:
    bad = _qa_ok()
    del bad["naturalness"]
    with pytest.raises(ValidationError):
        item_from_dict(_base_item(qa=bad))


def test_complete_matched_group_helper() -> None:
    assert is_complete_matched_group(_full_group())
    # Drop one cell -> not complete.
    assert not is_complete_matched_group(_full_group()[:3])


def _manifest(**overrides: object) -> RunManifest:
    base: dict[str, object] = dict(
        experiment_id="ASCR-pilot",
        shard_id="ASCR-Mini-0",
        prompt_set_version="unc-v1",
        model_name="Qwen/Qwen2.5-7B-Instruct",
        model_revision="deadbeefcafe",
        tokenizer_revision="tok-1",
        chat_template="qwen-chatml",
        code_commit="abc1234",
        seed=0,
        decoding={"temperature": 0.0},
        layer=16,
        token_position="prompt_final",
        stimulus_file_hash="sha256:aaa",
        environment="py3.11-linux",
        timestamp="2026-07-12T00:00:00Z",
    )
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
    # Different shard id / seed / stimulus / timestamp are still combinable.
    b = _manifest(shard_id="ASCR-Mini-1", seed=3, stimulus_file_hash="sha256:bbb",
                  timestamp="2026-07-12T01:00:00Z")
    assert manifests_compatible(a, b)
    # Different model revision breaks compatibility.
    c = _manifest(model_revision="0000000")
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
        stray = [
            p.name
            for p in d.iterdir()
            if p.is_file() and p.name != "README.md"
        ]
        assert stray == [], f"unexpected non-README files in {sub}: {stray}"
