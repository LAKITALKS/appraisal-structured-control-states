"""Canonical labels for the ASCR pilot.

This module is the single source of truth for the response-strategy labels, the
2x2 design-cell labels, the candidate appraisal axes, and the pilot domains. The
prose taxonomy in ``preregistration/response-strategy-taxonomy.md`` mirrors the
``RESPONSE_STRATEGIES`` defined here; the unit tests keep the two consistent.

No model is run here. These are design-time vocabularies only.
"""

from __future__ import annotations

from typing import Final

# ---------------------------------------------------------------------------
# Response strategies (the target variable: a higher-level policy mode).
# Meaning-based; NOT keyword-based. See the taxonomy document for definitions.
# ---------------------------------------------------------------------------
RESPONSE_STRATEGIES: Final[tuple[str, ...]] = (
    "direct_compliance",
    "calibrated_answer",
    "hedging",
    "clarification_request",
    "warning",
    "correction",
    "abstention",
    "refusal",
    "conditional_continuation",
)

# ---------------------------------------------------------------------------
# The 2x2 design cells: actual task state x appraisal-concept mention.
# ---------------------------------------------------------------------------
# Keyed by (task_state_present, concept_mention_present).
DESIGN_CELLS: Final[dict[tuple[bool, bool], str]] = {
    (False, False): "A_neutral_control",
    (False, True): "B_concept_tracking_only",
    (True, False): "C_pure_task_induction",
    (True, True): "D_combined",
}

# ---------------------------------------------------------------------------
# Candidate appraisal axes. Primary axes drive the pilot; the others are
# exploratory and are not load-bearing for the primary analysis.
# ---------------------------------------------------------------------------
PRIMARY_AXES: Final[tuple[str, ...]] = (
    "uncertainty",
    "norm_tension",
    "controllability",
)

EXPLORATORY_AXES: Final[tuple[str, ...]] = (
    "signed_relevance",
    "goal_congruence",
    "response_pressure",
)

AXES: Final[tuple[str, ...]] = PRIMARY_AXES + EXPLORATORY_AXES

# ---------------------------------------------------------------------------
# Pilot domains (semantically distinct; no single sensitive topic dominates).
# ---------------------------------------------------------------------------
DOMAINS: Final[tuple[str, ...]] = (
    "software_debugging",
    "scheduling_planning",
    "policy_constrained_assistance",
    "document_editing",
)


def design_cell(task_state_present: bool, concept_mention_present: bool) -> str:
    """Return the design-cell label for the two design factors."""
    return DESIGN_CELLS[(bool(task_state_present), bool(concept_mention_present))]


def is_valid_strategy(label: str) -> bool:
    """True if ``label`` is a known response strategy."""
    return label in RESPONSE_STRATEGIES


def is_primary_axis(axis: str) -> bool:
    """True if ``axis`` is one of the primary (load-bearing) pilot axes."""
    return axis in PRIMARY_AXES
