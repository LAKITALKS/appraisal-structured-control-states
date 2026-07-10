"""Tests for the ASCR prompt-item schema and config validation."""

from __future__ import annotations

import pytest

from ascr import schema
from ascr.schema import (
    PromptItem,
    ValidationError,
    item_from_dict,
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
        "model": {
            "name": "Qwen/Qwen2.5-7B-Instruct",
            "revision": "TO_BE_FROZEN_BEFORE_DATA_GENERATION",
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
        parse_config({"model": {"name": "x", "revision": "y"}})


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
