"""Tests for the canonical ASCR labels."""

from __future__ import annotations

import pytest

from ascr import strategy_labels as sl


def test_response_strategies_are_unique_and_nonempty() -> None:
    assert sl.RESPONSE_STRATEGIES  # non-empty
    assert len(sl.RESPONSE_STRATEGIES) == len(set(sl.RESPONSE_STRATEGIES))


def test_taxonomy_matches_documented_labels() -> None:
    # Keep code and the prose taxonomy in sync. If the taxonomy doc changes, this
    # explicit list must change with it.
    expected = {
        "direct_compliance",
        "calibrated_answer",
        "hedging",
        "clarification_request",
        "warning",
        "correction",
        "abstention",
        "refusal",
        "conditional_continuation",
    }
    assert set(sl.RESPONSE_STRATEGIES) == expected


def test_design_cells_cover_the_full_2x2() -> None:
    keys = set(sl.DESIGN_CELLS)
    assert keys == {(False, False), (False, True), (True, False), (True, True)}
    assert len(set(sl.DESIGN_CELLS.values())) == 4


@pytest.mark.parametrize(
    "task_state,concept,expected_prefix",
    [
        (False, False, "A_"),
        (False, True, "B_"),
        (True, False, "C_"),
        (True, True, "D_"),
    ],
)
def test_design_cell_labels(task_state: bool, concept: bool, expected_prefix: str) -> None:
    assert sl.design_cell(task_state, concept).startswith(expected_prefix)


def test_primary_axes_are_subset_of_axes() -> None:
    assert set(sl.PRIMARY_AXES).issubset(set(sl.AXES))
    assert set(sl.EXPLORATORY_AXES).issubset(set(sl.AXES))
    assert set(sl.PRIMARY_AXES).isdisjoint(set(sl.EXPLORATORY_AXES))


def test_axis_and_strategy_helpers() -> None:
    assert sl.is_primary_axis("uncertainty")
    assert not sl.is_primary_axis("goal_congruence")
    assert sl.is_valid_strategy("refusal")
    assert not sl.is_valid_strategy("not_a_strategy")
