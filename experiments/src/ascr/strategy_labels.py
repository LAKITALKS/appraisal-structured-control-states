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
# Two-tier taxonomy (v0.1.1 amendment): four primary superclasses used for the
# primary pilot analysis. The nine fine labels above are retained for the
# secondary and qualitative analysis. Every fine label maps to exactly one
# superclass; the mapping is checked by the unit tests.
# ---------------------------------------------------------------------------
STRATEGY_SUPERCLASSES: Final[tuple[str, ...]] = (
    "direct_or_comply",
    "qualify_or_warn",
    "redirect_or_clarify",
    "decline_or_abstain",
)

FINE_TO_SUPERCLASS: Final[dict[str, str]] = {
    "direct_compliance": "direct_or_comply",
    "calibrated_answer": "qualify_or_warn",
    "hedging": "qualify_or_warn",
    "warning": "qualify_or_warn",
    "correction": "qualify_or_warn",
    "clarification_request": "redirect_or_clarify",
    "conditional_continuation": "redirect_or_clarify",
    "abstention": "decline_or_abstain",
    "refusal": "decline_or_abstain",
}


def superclass_of(fine_label: str) -> str:
    """Return the primary superclass for a fine-grained response strategy."""
    try:
        return FINE_TO_SUPERCLASS[fine_label]
    except KeyError as exc:  # pragma: no cover - defensive
        raise KeyError(f"unknown fine label {fine_label!r}") from exc


# Dominance ordering for tie-breaking when a response exhibits several acts
# (highest priority first). See preregistration/response-strategy-taxonomy.md.
SUPERCLASS_DOMINANCE: Final[tuple[str, ...]] = (
    "decline_or_abstain",
    "redirect_or_clarify",
    "qualify_or_warn",
    "direct_or_comply",
)


def dominant_superclass(fine_labels: "list[str] | tuple[str, ...] | set[str]") -> str:
    """Return the dominant superclass for a set of candidate fine labels.

    Deterministic tie-breaker (not a generative classifier): map each candidate
    fine label to its superclass, then pick the highest-priority superclass per
    ``SUPERCLASS_DOMINANCE``. Raises on an empty or unknown input.
    """
    labels = list(fine_labels)
    if not labels:
        raise ValueError("dominant_superclass requires at least one fine label")
    present = {superclass_of(f) for f in labels}
    for sup in SUPERCLASS_DOMINANCE:
        if sup in present:
            return sup
    raise AssertionError("unreachable: every superclass is in SUPERCLASS_DOMINANCE")


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
