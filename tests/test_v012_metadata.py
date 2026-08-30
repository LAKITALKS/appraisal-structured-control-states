"""Configuration, QA, metadata, and no-data guards for v0.1.2."""

from __future__ import annotations

import json
import pathlib
import tomllib

import pytest
import yaml

import ascr
from ascr.schema import (
    QA_BOOLEAN_FIELDS,
    ValidationError,
    config_can_generate_scientific_data,
    config_run_ready_problems,
    item_from_dict,
    load_config,
    parse_config,
)

REPO = pathlib.Path(__file__).resolve().parents[1]


def _qa(task: bool, concept: bool, **overrides: object) -> dict[str, object]:
    qa: dict[str, object] = {name: True for name in QA_BOOLEAN_FIELDS}
    qa.update(
        naturalness_rating=5,
        observed_task_state_present=task,
        observed_concept_mention_present=concept,
        non_target_axes_absent_confirmed={
            "norm_tension": True,
            "controllability": True,
        },
        reviewer_id="reviewer-1",
        review_timestamp="2026-08-30T00:00:00Z",
        disposition="pass",
    )
    qa.update(overrides)
    return qa


def _item(task: bool, concept: bool, qa: dict[str, object]):
    return item_from_dict(
        {
            "item_id": f"unc-dbg-{int(task)}{int(concept)}",
            "axis": "uncertainty",
            "domain": "software_debugging",
            "task_state_present": task,
            "concept_mention_present": concept,
            "prompt_text": "Design-only prompt.",
            "matched_group_id": "unc-dbg-1",
            "expected_strategy_space": ["clarification_request"],
            "qa": qa,
        }
    )


def test_v012_config_parses_and_draft_cannot_generate_data() -> None:
    cfg = load_config(REPO / "experiments/configs/pilot.yaml")
    assert cfg.config_version == "0.1.2"
    assert cfg.validation_mode == "draft"
    assert not config_can_generate_scientific_data(cfg)


def test_historical_v011_config_remains_identifiable_but_not_run_ready() -> None:
    cfg = parse_config(
        {
            "config_version": "0.1.1",
            "model": {
                "name": "Qwen/Qwen2.5-7B-Instruct",
                "revision": "historical-sha",
                "replication_model": "TO_BE_SELECTED_BEFORE_CONFIRMATORY_REPLICATION",
            },
            "design": {"axes": ["uncertainty"], "domains": list(ascr.DOMAINS)},
            "activations": {"layers": "all"},
            "analysis": {"seeds": [0]},
        }
    )
    assert cfg.is_historical
    assert any("historical v0.1.1" in p for p in config_run_ready_problems(cfg))


def test_all_run_revision_and_embedding_sentinels_block_current_config() -> None:
    problems = config_run_ready_problems(
        load_config(REPO / "experiments/configs/pilot.yaml")
    )
    for expected in (
        "model revision",
        "tokenizer revision",
        "prompt-embedding model",
        "prompt-embedding revision",
        "prompt-embedding license",
        "prompt-embedding pooling rule",
        "author approval",
        "layer candidate grid",
        "H1 layer/position FDR family",
    ):
        assert any(expected in problem for problem in problems), (expected, problems)


def test_factor_values_are_checked_for_a_b_c_d_not_forced_true() -> None:
    # A/B correctly record an absent target state; C/D correctly record presence.
    _item(False, False, _qa(False, False)).validate(mode="run_ready")
    _item(True, True, _qa(True, True)).validate(mode="run_ready")
    wrong = _item(True, False, _qa(False, False))
    with pytest.raises(ValidationError):
        wrong.validate(mode="run_ready")


def test_non_target_axis_confirmations_are_exact_and_required() -> None:
    missing = _item(
        True,
        False,
        _qa(True, False, non_target_axes_absent_confirmed={"norm_tension": True}),
    )
    with pytest.raises(ValidationError):
        missing.validate(mode="run_ready")
    failed = _item(
        True,
        False,
        _qa(
            True,
            False,
            non_target_axes_absent_confirmed={
                "norm_tension": True,
                "controllability": False,
            },
        ),
    )
    with pytest.raises(ValidationError):
        failed.validate(mode="run_ready")


def test_legacy_qa_is_readable_in_draft_but_not_v012_run_ready() -> None:
    legacy = {"grammatical": True, "primary_axis_isolated": True}
    item = _item(True, False, legacy)
    item.validate(mode="draft")
    with pytest.raises(ValidationError):
        item.validate(mode="run_ready")


def test_versions_and_authorship_metadata_are_consistent() -> None:
    pyproject = tomllib.loads((REPO / "pyproject.toml").read_text())
    cff = yaml.safe_load((REPO / "CITATION.cff").read_text())
    zenodo = json.loads((REPO / ".zenodo.json").read_text())
    assert pyproject["project"]["version"] == "0.1.2"
    assert cff["version"] == "0.1.2"
    assert zenodo["version"] == "0.1.2"
    assert ascr.__version__ == "0.1.2"
    assert cff["type"] == "software"
    assert len(cff["authors"]) == 1
    assert len(cff["preferred-citation"]["authors"]) == 1
    assert len(zenodo["creators"]) == 1
    serialized = json.dumps({"cff": cff, "zenodo": zenodo}).lower()
    assert "orcid" not in serialized


def test_historical_dois_preserved_and_v012_unreleased() -> None:
    text = (REPO / "README.md").read_text()
    assert "10.5281/zenodo.21294932" in text
    assert "10.5281/zenodo.21294933" in text
    assert "10.5281/zenodo.21335529" in text
    cff = yaml.safe_load((REPO / "CITATION.cff").read_text())
    assert "date-released" not in cff
    assert "doi" not in cff["preferred-citation"]


def test_no_scientific_artifacts_exist() -> None:
    for subdir in ("experiments/data", "experiments/results"):
        files = [p.name for p in (REPO / subdir).iterdir() if p.is_file()]
        assert files == ["README.md"]
