"""Typed schema and validation for ASCR pilot prompt items.

This scaffold does *not* run the model experiment. It defines the metadata every
prompt item must carry so that the 2x2 design (actual task state x appraisal
concept mention) is well formed and machine-checkable before any activations are
extracted, and it freezes the v0.1.2 statistical specification so that it can be
checked mechanically rather than only in prose.

Everything here is a **design-time guard**: these functions read configuration,
stimulus metadata, and manifests, and they never construct, download, load, or
execute a model, and never produce data. The single entry point a future
extraction runner must clear before it constructs or loads any model, tokenizer,
or prompt-embedding model is :func:`integrated_pre_run_gate_problems`, which must
return an empty list.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Final

from .strategy_labels import (
    AXES,
    DOMAINS,
    PRIMARY_AXES,
    RESPONSE_STRATEGIES,
    STRATEGY_SUPERCLASSES,
    design_cell,
)


class ValidationError(ValueError):
    """Raised when a prompt item or config fails schema validation."""


# Sentinels that must be replaced before the first data collection / replication.
PLACEHOLDER_MODEL_REVISION = "TO_BE_FROZEN_BEFORE_DATA_GENERATION"
PLACEHOLDER_TOKENIZER_REVISION = "TO_BE_FROZEN_BEFORE_DATA_GENERATION"
PLACEHOLDER_EMBEDDING_MODEL = "TO_BE_SELECTED_BY_AUTHOR_BEFORE_MINI_0"
PLACEHOLDER_EMBEDDING_REVISION = "TO_BE_FROZEN_AFTER_AUTHOR_SELECTION"
PLACEHOLDER_REPLICATION_MODEL = "TO_BE_SELECTED_BEFORE_CONFIRMATORY_REPLICATION"
PLACEHOLDER_LAYER_CANDIDATES = "TO_BE_FROZEN_BEFORE_MINI_0"
PLACEHOLDER_POSITION_CANDIDATES = "TO_BE_FROZEN_BEFORE_MINI_0"
SUPPORTED_CONFIG_VERSIONS: tuple[str, ...] = ("0.1.1", "0.1.2")

# The only value that may stand in for a prompt-embedding manifest field, and only
# in a `technical_smoke` manifest that uses no prompt-embedding model at all. A
# scientific manifest must carry a real, frozen, immutable value instead.
NOT_APPLICABLE_TECHNICAL_SMOKE = "NOT_APPLICABLE_TECHNICAL_SMOKE"

# Immutable revision format required for every scientific run: the full
# hexadecimal commit revision (40 lowercase hex characters), never a short prefix,
# a branch name, or a tag that can move.
IMMUTABLE_REVISION_PATTERN: Final[re.Pattern[str]] = re.compile(r"^[0-9a-f]{40}$")

# Explicit format for every recorded SHA-256 digest field.
SHA256_FIELD_PATTERN: Final[re.Pattern[str]] = re.compile(r"^sha256:[0-9a-f]{64}$")

# ---------------------------------------------------------------------------
# Frozen v0.1.2 statistical specification (pre-data; see
# preregistration/amendment-v0.1.2.md and analysis-plan.md).
# ---------------------------------------------------------------------------
H1_TARGET: Final[str] = "task_state_present"
H2_TARGET: Final[str] = "response_strategy_superclass"
H2_PRIMARY_ESTIMAND: Final[str] = (
    "log_loss_prompt_embedding_minus_log_loss_hidden_state"
)
H2_SIGN_CONVENTION: Final[str] = "positive_favors_hidden_state"
H2_SECONDARY_SIGN_CONVENTION: Final[str] = (
    "balanced_accuracy_hidden_state_minus_prompt_embedding"
)
H2_DECISION_RULES: Final[tuple[str, ...]] = (
    "positive_rule",
    "weakened_rule",
    "indeterminate_rule",
)
NOT_ESTIMABLE: Final[str] = "NOT_ESTIMABLE"

#: Frozen logistic-regression regularization grid. Never selected after data exist.
REGULARIZATION_C_GRID: Final[tuple[float, ...]] = (
    1e-4,
    1e-3,
    1e-2,
    1e-1,
    1.0,
    10.0,
    100.0,
)
#: Frozen seed roles. Only the primary seed produces decision statistics.
PRIMARY_SEED: Final[int] = 0
SENSITIVITY_SEEDS: Final[tuple[int, ...]] = (1, 2, 3, 4)
BOOTSTRAP_SEED: Final[int] = 20260830
PERMUTATION_SEED: Final[int] = 20260831
#: Frozen Benjamini-Hochberg false-discovery rate.
BH_Q: Final[float] = 0.05

# --- Concept-mention / naturalness QA schema (strengthened in v0.1.2) ---
#
# Two validation modes: "draft" (incomplete QA allowed; NO activation extraction)
# and "run_ready" (complete, typed QA required before any real run).
QA_MODES: tuple[str, ...] = ("draft", "run_ready")

# Scientific authorization is stage-specific. Mini-0 does not depend on the later
# intervention grid; H3 does. Keeping the stage explicit prevents a deferred H3
# choice from either blocking Mini-0 or being silently treated as already frozen.
RUN_GATE_STAGES: tuple[str, ...] = ("mini0_scientific", "h3_intervention")
MINI0_GATE_STAGE: Final[str] = "mini0_scientific"
H3_GATE_STAGE: Final[str] = "h3_intervention"
MINI0_SHARD_ID: Final[str] = "ASCR-Mini-0"
MINI0_TARGET_AXIS: Final[str] = "uncertainty"
RUN_PLAN_FROZEN_STATUS: Final[str] = "FROZEN_PRE_DATA"
RESPONSE_LABEL_RELIABILITY_SEED: Final[int] = 20260901
RESPONSE_LABEL_RELIABILITY_BOOTSTRAP_SEED: Final[int] = 20260902
RESPONSE_LABEL_RELIABILITY_FRACTION: Final[float] = 0.30
RESPONSE_LABEL_RELIABILITY_KAPPA_THRESHOLD: Final[float] = 0.60

# Boolean QA flags that must all be True for an item to pass.
QA_BOOLEAN_FIELDS: tuple[str, ...] = (
    "grammatical",
    "register_match",
    "domain_match",
    "target_task_match",
    "solvable_as_intended",
    "label_leak_free",
    "no_artificial_meta_sentence",
    "primary_axis_isolated",
)
QA_DESIGN_VALUE_FIELDS: tuple[str, ...] = (
    "observed_task_state_present",
    "observed_concept_mention_present",
)
QA_AXIS_ABSENCE_FIELD = "non_target_axes_absent_confirmed"
QA_DISPOSITIONS: tuple[str, ...] = ("pass", "revise", "discard")
QA_MIN_NATURALNESS = 4
QA_MAX_GROUP_NATURALNESS_SPREAD = 1

# All fields a run_ready QA record must contain.
REQUIRED_QA_FIELDS: tuple[str, ...] = (
    ("naturalness_rating",)
    + QA_BOOLEAN_FIELDS
    + QA_DESIGN_VALUE_FIELDS
    + (
        QA_AXIS_ABSENCE_FIELD,
        "reviewer_id",
        "review_timestamp",
        "disposition",
    )
)

# External-data provenance fields (v0.1.1 amendment, item 6).
EXTERNAL_PROVENANCE_FIELDS: tuple[str, ...] = (
    "dataset_name",
    "version",
    "split",
    "original_id",
    "license",
    "source",
    "retrieval_date",
    "original_label",
    "human_reviewed_label",
    "reviewer_id",
    "adjustments",
    "contamination_risk",
    "decision",
)
PROVENANCE_DECISIONS: tuple[str, ...] = ("include", "revise", "exclude")


def is_placeholder_revision(revision: str) -> bool:
    """True if ``revision`` is still an unfilled placeholder (not a frozen hash)."""
    return revision == PLACEHOLDER_MODEL_REVISION or revision.startswith("TO_BE_")


def _is_unfrozen_value(value: Any) -> bool:
    """True for empty or recursively placeholder-bearing pre-data values."""

    if value is None:
        return True
    if isinstance(value, str):
        return not value.strip() or value.startswith("TO_BE_")
    if isinstance(value, dict):
        return not value or any(_is_unfrozen_value(v) for v in value.values())
    if isinstance(value, (list, tuple)):
        return not value or any(_is_unfrozen_value(v) for v in value)
    return False


def _is_iso8601(value: Any) -> bool:
    if not isinstance(value, str) or not value:
        return False
    from datetime import datetime

    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
        return True
    except ValueError:
        return False


def validate_qa(
    qa: dict[str, Any], item_id: str = "<item>", *, mode: str = "draft"
) -> None:
    """Validate a QA record.

    ``mode="draft"`` only requires a mapping (incomplete QA is allowed during
    authoring). ``mode="run_ready"`` enforces the full typed schema.
    """
    if mode not in QA_MODES:
        raise ValidationError(f"unknown QA mode {mode!r}")
    if not isinstance(qa, dict):
        raise ValidationError(f"{item_id}: qa must be a mapping")
    if mode == "draft":
        return

    missing = [k for k in REQUIRED_QA_FIELDS if k not in qa]
    if missing:
        raise ValidationError(f"{item_id}: run_ready qa missing fields {missing}")

    rating = qa["naturalness_rating"]
    if (
        not isinstance(rating, int)
        or isinstance(rating, bool)
        or not (1 <= rating <= 5)
    ):
        raise ValidationError(
            f"{item_id}: naturalness_rating must be an int in 1..5, got {rating!r}"
        )
    for name in QA_BOOLEAN_FIELDS:
        if not isinstance(qa[name], bool):
            raise ValidationError(f"{item_id}: qa.{name} must be a bool")
    for name in QA_DESIGN_VALUE_FIELDS:
        if not isinstance(qa[name], bool):
            raise ValidationError(f"{item_id}: qa.{name} must be a bool")
    axis_absence = qa[QA_AXIS_ABSENCE_FIELD]
    if not isinstance(axis_absence, dict):
        raise ValidationError(
            f"{item_id}: qa.{QA_AXIS_ABSENCE_FIELD} must be a mapping"
        )
    if any(
        not isinstance(k, str) or not isinstance(v, bool)
        for k, v in axis_absence.items()
    ):
        raise ValidationError(
            f"{item_id}: qa.{QA_AXIS_ABSENCE_FIELD} must map axis names to bools"
        )
    _require_nonempty_str(qa["reviewer_id"], f"{item_id}: qa.reviewer_id")
    if not _is_iso8601(qa["review_timestamp"]):
        raise ValidationError(
            f"{item_id}: qa.review_timestamp must be an ISO-8601 string"
        )
    if qa["disposition"] not in QA_DISPOSITIONS:
        raise ValidationError(
            f"{item_id}: qa.disposition must be one of {QA_DISPOSITIONS}"
        )


def qa_item_passes(
    qa: dict[str, Any],
    *,
    task_state_present: bool | None = None,
    concept_mention_present: bool | None = None,
    target_axis: str | None = None,
) -> bool:
    """True if a typed QA record meets the v0.1.2 item-level pass criteria.

    Historical draft QA can still be read, but a run-ready item supplies its
    registered factor values and target axis so that A/B and C/D are checked
    correctly and the other primary axes are explicitly confirmed absent.
    """
    try:
        validate_qa(qa, mode="run_ready")
    except ValidationError:
        return False
    if qa["disposition"] != "pass":
        return False
    if any(qa[name] is not True for name in QA_BOOLEAN_FIELDS):
        return False
    if task_state_present is not None and (
        qa["observed_task_state_present"] is not task_state_present
    ):
        return False
    if concept_mention_present is not None and (
        qa["observed_concept_mention_present"] is not concept_mention_present
    ):
        return False
    if target_axis is not None:
        expected_absent = set(PRIMARY_AXES) - (
            {target_axis} if target_axis in PRIMARY_AXES else set()
        )
        confirmations = qa[QA_AXIS_ABSENCE_FIELD]
        if set(confirmations) != expected_absent:
            return False
        if any(confirmations[axis] is not True for axis in expected_absent):
            return False
    return qa["naturalness_rating"] >= QA_MIN_NATURALNESS


def validate_provenance(record: dict[str, Any], item_id: str = "<item>") -> None:
    """Validate an external-data provenance record (presence + decision enum)."""
    if not isinstance(record, dict):
        raise ValidationError(f"{item_id}: provenance must be a mapping")
    missing = [k for k in EXTERNAL_PROVENANCE_FIELDS if k not in record]
    if missing:
        raise ValidationError(f"{item_id}: provenance missing fields {missing}")
    if record["decision"] not in PROVENANCE_DECISIONS:
        raise ValidationError(
            f"{item_id}: provenance.decision must be one of {PROVENANCE_DECISIONS}"
        )


def provenance_is_run_ready(record: dict[str, Any]) -> bool:
    """True if an external item has been human-reviewed and approved for inclusion."""
    try:
        validate_provenance(record)
    except ValidationError:
        return False
    if record["decision"] != "include":
        return False
    return (
        isinstance(record.get("human_reviewed_label"), str)
        and bool(record["human_reviewed_label"].strip())
        and isinstance(record.get("reviewer_id"), str)
        and bool(record["reviewer_id"].strip())
    )


@dataclass(frozen=True, slots=True)
class PromptItem:
    """A single pilot prompt in one cell of the 2x2 design.

    Fields
    ------
    item_id:
        Unique identifier for this item.
    axis:
        Candidate appraisal axis (see ``strategy_labels.AXES``).
    domain:
        Semantic domain (see ``strategy_labels.DOMAINS``).
    task_state_present:
        Whether the model's *own* task actually contains the property
        (ambiguity, conflict, low controllability, ...).
    concept_mention_present:
        Whether appraisal-related *vocabulary* appears in the prompt.
    prompt_text:
        The prompt shown to the model.
    matched_group_id:
        Groups the A/B/C/D siblings built from one base task; splits are made at
        this level so siblings never straddle train/test.
    expected_strategy_space:
        The plausible response strategies for this item (subset of
        ``RESPONSE_STRATEGIES``); must be non-empty.
    notes:
        Free-form construction notes (optional).
    qa:
        Concept-mention / naturalness QA record (optional in draft mode, required
        and typed in run_ready mode).
    provenance:
        External-data provenance record (only for items adapted from external
        datasets); must be human-reviewed before a run.
    """

    item_id: str
    axis: str
    domain: str
    task_state_present: bool
    concept_mention_present: bool
    prompt_text: str
    matched_group_id: str
    expected_strategy_space: tuple[str, ...]
    notes: str = ""
    qa: dict[str, Any] | None = None
    provenance: dict[str, Any] | None = None

    @property
    def cell(self) -> str:
        """The design-cell label derived from the two design factors."""
        return design_cell(self.task_state_present, self.concept_mention_present)

    def validate(self, *, mode: str = "draft") -> None:
        """Raise :class:`ValidationError` if any required metadata is invalid.

        ``mode="run_ready"`` additionally enforces the full typed QA schema and the
        item-level QA pass criteria.
        """
        _require_nonempty_str(self.item_id, "item_id")
        _require_nonempty_str(self.prompt_text, "prompt_text")
        _require_nonempty_str(self.matched_group_id, "matched_group_id")
        if self.qa is not None:
            validate_qa(self.qa, self.item_id, mode=mode)
        if self.provenance is not None:
            validate_provenance(self.provenance, self.item_id)
        if mode == "run_ready":
            if self.qa is None:
                raise ValidationError(
                    f"{self.item_id}: run_ready requires a complete QA record"
                )
            if not qa_item_passes(
                self.qa,
                task_state_present=self.task_state_present,
                concept_mention_present=self.concept_mention_present,
                target_axis=self.axis,
            ):
                raise ValidationError(
                    f"{self.item_id}: QA does not pass "
                    "(factor values/axis isolation/disposition/flags/naturalness)"
                )
            if self.provenance is not None and not provenance_is_run_ready(
                self.provenance
            ):
                raise ValidationError(
                    f"{self.item_id}: external item is not review-approved for a run"
                )

        if self.axis not in AXES:
            raise ValidationError(
                f"{self.item_id}: unknown axis {self.axis!r}; expected one of {AXES}"
            )
        if self.domain not in DOMAINS:
            raise ValidationError(
                f"{self.item_id}: unknown domain {self.domain!r}; "
                f"expected one of {DOMAINS}"
            )
        if not isinstance(self.task_state_present, bool):
            raise ValidationError(f"{self.item_id}: task_state_present must be bool")
        if not isinstance(self.concept_mention_present, bool):
            raise ValidationError(
                f"{self.item_id}: concept_mention_present must be bool"
            )
        if not self.expected_strategy_space:
            raise ValidationError(
                f"{self.item_id}: expected_strategy_space must be non-empty"
            )
        unknown = [
            s for s in self.expected_strategy_space if s not in RESPONSE_STRATEGIES
        ]
        if unknown:
            raise ValidationError(
                f"{self.item_id}: unknown response strategies {unknown}"
            )


def _require_nonempty_str(value: Any, name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(f"{name} must be a non-empty string, got {value!r}")


def item_from_dict(data: dict[str, Any]) -> PromptItem:
    """Build and validate a :class:`PromptItem` from a plain dict.

    Unknown keys are rejected so that typos in the dataset surface early.
    """
    required = {
        "item_id",
        "axis",
        "domain",
        "task_state_present",
        "concept_mention_present",
        "prompt_text",
        "matched_group_id",
        "expected_strategy_space",
    }
    optional = {"notes", "qa", "provenance"}
    allowed = required | optional
    unknown_keys = set(data) - allowed
    if unknown_keys:
        raise ValidationError(f"unknown item fields: {sorted(unknown_keys)}")
    missing = required - set(data)
    if missing:
        raise ValidationError(f"missing required item fields: {sorted(missing)}")

    item = PromptItem(
        item_id=data["item_id"],
        axis=data["axis"],
        domain=data["domain"],
        task_state_present=data["task_state_present"],
        concept_mention_present=data["concept_mention_present"],
        prompt_text=data["prompt_text"],
        matched_group_id=data["matched_group_id"],
        expected_strategy_space=tuple(data["expected_strategy_space"]),
        notes=data.get("notes", ""),
        qa=data.get("qa"),
        provenance=data.get("provenance"),
    )
    item.validate()
    return item


def item_to_dict(item: PromptItem) -> dict[str, Any]:
    """Serialize a prompt item without weakening its typed nested metadata."""

    item.validate()
    result: dict[str, Any] = {
        "item_id": item.item_id,
        "axis": item.axis,
        "domain": item.domain,
        "task_state_present": item.task_state_present,
        "concept_mention_present": item.concept_mention_present,
        "prompt_text": item.prompt_text,
        "matched_group_id": item.matched_group_id,
        "expected_strategy_space": list(item.expected_strategy_space),
        "notes": item.notes,
    }
    if item.qa is not None:
        result["qa"] = dict(item.qa)
    if item.provenance is not None:
        result["provenance"] = dict(item.provenance)
    return result


def validate_matched_group(items: list[PromptItem]) -> None:
    """Validate a set of siblings sharing a ``matched_group_id``.

    A complete matched group covers all four 2x2 cells exactly once for a single
    (axis, domain) pair. Partial groups are allowed during authoring but flagged.
    """
    if not items:
        raise ValidationError("matched group is empty")
    for item in items:
        item.validate()

    group_ids = {item.matched_group_id for item in items}
    if len(group_ids) != 1:
        raise ValidationError(f"mixed matched_group_id values: {sorted(group_ids)}")

    axes = {item.axis for item in items}
    domains = {item.domain for item in items}
    if len(axes) != 1 or len(domains) != 1:
        raise ValidationError(
            "a matched group must share one axis and one domain; "
            f"got axes={sorted(axes)} domains={sorted(domains)}"
        )

    cells = [item.cell for item in items]
    if len(cells) != len(set(cells)):
        raise ValidationError(f"duplicate design cells in matched group: {cells}")


def is_complete_matched_group(items: list[PromptItem]) -> bool:
    """True if the group covers all four 2x2 cells exactly once and validates."""
    try:
        validate_matched_group(items)
    except ValidationError:
        return False
    return {item.cell for item in items} == set(design_cell_labels())


def design_cell_labels() -> tuple[str, ...]:
    """The four 2x2 design-cell labels (A/B/C/D)."""
    from .strategy_labels import DESIGN_CELLS

    return tuple(DESIGN_CELLS.values())


# ---------------------------------------------------------------------------
# Run-ready gate (strengthened in v0.1.2). NO run may proceed unless the whole
# stimulus set is run_ready. Draft items are for authoring only.
# ---------------------------------------------------------------------------
def validate_run_ready_group(items: list[PromptItem]) -> None:
    """Validate that a matched group is fully run_ready.

    Requires a complete A/B/C/D group, each item passing run_ready QA, and a
    within-group naturalness spread of at most one scale point.
    """
    if not is_complete_matched_group(items):
        raise ValidationError(
            f"matched group is not a complete A/B/C/D set: "
            f"{sorted(i.cell for i in items)}"
        )
    for item in items:
        item.validate(mode="run_ready")
    ratings = [int(item.qa["naturalness_rating"]) for item in items]  # type: ignore[index]
    if max(ratings) - min(ratings) > QA_MAX_GROUP_NATURALNESS_SPREAD:
        raise ValidationError(
            "within-group naturalness spread exceeds "
            f"{QA_MAX_GROUP_NATURALNESS_SPREAD} point(s): {ratings}"
        )


def canonical_stimulus_hash(items: list[PromptItem]) -> str:
    """Return the SHA-256 of the canonical, order-independent stimulus payload.

    The scientific gate compares this digest with both the frozen run plan and the
    run manifest. It hashes the complete typed item records rather than a YAML
    file's incidental whitespace or key order.
    """

    payload = [item_to_dict(item) for item in sorted(items, key=lambda x: x.item_id)]
    encoded = json.dumps(
        payload,
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ":"),
    ).encode("utf-8")
    return f"sha256:{hashlib.sha256(encoded).hexdigest()}"


def check_run_ready(
    items: list[PromptItem],
    *,
    model_revision: str | None = None,
    tokenizer_revision: str | None = None,
    prompt_embedding_model: str | None = None,
    prompt_embedding_revision: str | None = None,
    min_complete_groups: int | None = None,
    target_axis: str | None = None,
    required_domains: tuple[str, ...] | None = None,
    require_balanced_domains: bool = False,
) -> list[str]:
    """Return a list of run-readiness problems (empty list == run_ready).

    A CLI-validatable routine over a whole stimulus set. It blocks a run when: any
    matched group is not run_ready; the model revision is still a placeholder; the
    number of complete run_ready groups is below the configured sample size; or an
    external item has not been review-approved.
    """
    problems: list[str] = []
    groups: dict[str, list[PromptItem]] = {}
    seen_item_ids: set[str] = set()
    for item in items:
        if item.item_id in seen_item_ids:
            problems.append(f"duplicate item_id {item.item_id!r}")
        seen_item_ids.add(item.item_id)
        groups.setdefault(item.matched_group_id, []).append(item)

    complete = 0
    run_ready_group_domains: dict[str, str] = {}
    for gid, gitems in sorted(groups.items()):
        try:
            validate_run_ready_group(gitems)
            complete += 1
            run_ready_group_domains[gid] = gitems[0].domain
        except ValidationError as exc:
            problems.append(f"group {gid}: {exc}")

    for label, revision in (
        ("model revision", model_revision),
        ("tokenizer revision", tokenizer_revision),
        ("prompt-embedding revision", prompt_embedding_revision),
    ):
        if revision is not None and not is_immutable_revision(revision):
            problems.append(
                f"{label} is a placeholder or nonimmutable value; it must be a "
                "full immutable 40-character lowercase "
                "hexadecimal commit revision"
            )
    if prompt_embedding_model is not None and is_placeholder_revision(
        prompt_embedding_model
    ):
        problems.append(
            "prompt-embedding model is still an author-decision placeholder"
        )
    if min_complete_groups is not None and complete < min_complete_groups:
        problems.append(
            f"only {complete} complete run_ready matched groups; "
            f"sample-size gate requires >= {min_complete_groups}"
        )
    for item in items:
        if item.provenance is not None and not provenance_is_run_ready(item.provenance):
            problems.append(
                f"{item.item_id}: external item not review-approved (provenance)"
            )
    observed_axes = {item.axis for item in items}
    if target_axis is not None:
        if target_axis not in PRIMARY_AXES:
            problems.append(
                f"target axis {target_axis!r} is not a registered primary axis"
            )
        if observed_axes != {target_axis}:
            problems.append(
                "stimulus set must contain exactly the frozen target axis; "
                f"observed={sorted(observed_axes)} expected={[target_axis]}"
            )
    elif len(observed_axes) > 1:
        problems.append(
            "stimulus set mixes axes; every scientific shard must declare one target axis"
        )

    if required_domains is not None:
        complete_by_domain = {domain: 0 for domain in required_domains}
        for domain in run_ready_group_domains.values():
            if domain in complete_by_domain:
                complete_by_domain[domain] += 1
        observed_domains = {item.domain for item in items}
        if observed_domains != set(required_domains):
            problems.append(
                "stimulus set must contain exactly all registered domains; "
                f"observed={sorted(observed_domains)} "
                f"expected={sorted(required_domains)}"
            )
        if any(count == 0 for count in complete_by_domain.values()):
            problems.append(
                "each registered domain must contribute at least one complete "
                "run_ready matched group"
            )
        if require_balanced_domains and complete_by_domain:
            counts = tuple(complete_by_domain.values())
            if max(counts) - min(counts) > 1:
                problems.append(
                    "complete matched-group counts must be evenly distributed across "
                    f"domains (max-min <= 1), got {complete_by_domain}"
                )
    return problems


def is_run_ready(
    items: list[PromptItem],
    *,
    model_revision: str | None = None,
    tokenizer_revision: str | None = None,
    prompt_embedding_model: str | None = None,
    prompt_embedding_revision: str | None = None,
    min_complete_groups: int | None = None,
    target_axis: str | None = None,
    required_domains: tuple[str, ...] | None = None,
    require_balanced_domains: bool = False,
) -> bool:
    """True if the whole stimulus set passes the run-ready gate."""
    return not check_run_ready(
        items,
        model_revision=model_revision,
        tokenizer_revision=tokenizer_revision,
        prompt_embedding_model=prompt_embedding_model,
        prompt_embedding_revision=prompt_embedding_revision,
        min_complete_groups=min_complete_groups,
        target_axis=target_axis,
        required_domains=required_domains,
        require_balanced_domains=require_balanced_domains,
    )


# ---------------------------------------------------------------------------
# Mini-shard and smoke-run manifests (v0.1.2 correction).
# ---------------------------------------------------------------------------
# Fields that must be identical for two shards to be safely combined. Each name
# appears exactly once (enforced below and by the unit tests): a repeated entry
# would silently weaken nothing but would misrepresent the registered field set.
#
# Intentionally excluded, and deliberately still combinable when they differ:
#   * ``timestamp``        - per-run wall-clock time;
#   * ``output_directory`` - per-run destination path;
#   * ``shard_id``         - shard identity is what combination ranges over;
#   * ``seed``             - the seed roles are fixed by the analysis plan, not by
#                            shard combinability.
_MANIFEST_COMPAT_FIELDS: tuple[str, ...] = (
    "experiment_id",
    "run_kind",
    "eligible_for_scientific_analysis",
    "target_axis",
    "prompt_set_id",
    "prompt_set_version",
    "stimulus_file_hash",
    "model_name",
    "model_revision",
    "tokenizer_revision",
    "prompt_embedding_model",
    "prompt_embedding_revision",
    "prompt_embedding_license",
    "prompt_embedding_pooling_rule",
    "prompt_embedding_truncation_rule",
    "prompt_embedding_max_input_length",
    "chat_template",
    "chat_template_hash",
    "code_commit",
    "decoding",
    "layer",
    "token_position",
    "environment",
)
if len(set(_MANIFEST_COMPAT_FIELDS)) != len(
    _MANIFEST_COMPAT_FIELDS
):  # pragma: no cover
    raise AssertionError("_MANIFEST_COMPAT_FIELDS must not contain duplicates")

_MANIFEST_EXCLUDED_COMPAT_FIELDS: tuple[str, ...] = (
    "timestamp",
    "output_directory",
    "shard_id",
    "seed",
)

#: Manifest fields that must carry a full immutable hexadecimal commit revision
#: before any scientific run.
IMMUTABLE_REVISION_FIELDS: tuple[str, ...] = (
    "model_revision",
    "tokenizer_revision",
    "prompt_embedding_revision",
    "code_commit",
)

#: Manifest fields recorded as an explicit ``sha256:<64 hex>`` digest.
SHA256_MANIFEST_FIELDS: tuple[str, ...] = (
    "stimulus_file_hash",
    "chat_template_hash",
)

#: Prompt-embedding manifest fields. Mandatory and frozen for a scientific run;
#: a technical smoke run that uses no prompt-embedding model may instead record
#: ``NOT_APPLICABLE_TECHNICAL_SMOKE`` explicitly.
PROMPT_EMBEDDING_MANIFEST_FIELDS: tuple[str, ...] = (
    "prompt_embedding_model",
    "prompt_embedding_revision",
    "prompt_embedding_license",
    "prompt_embedding_pooling_rule",
    "prompt_embedding_truncation_rule",
)

RUN_KINDS: tuple[str, ...] = ("technical_smoke", "scientific_feasibility")


def is_immutable_revision(value: str) -> bool:
    """True if ``value`` is a full 40-character lowercase hexadecimal revision."""
    return bool(IMMUTABLE_REVISION_PATTERN.match(value or ""))


def is_sha256_field(value: str) -> bool:
    """True if ``value`` has the registered ``sha256:<64 lowercase hex>`` form."""
    return bool(SHA256_FIELD_PATTERN.match(value or ""))


@dataclass(frozen=True, slots=True)
class RunManifest:
    """Immutable manifest recorded for one mini-shard run.

    No run is executed here; this only fixes which fields must be captured and
    which must match for shards to be combinable.
    """

    experiment_id: str
    shard_id: str
    run_kind: str
    eligible_for_scientific_analysis: bool
    target_axis: str
    prompt_set_id: str
    prompt_set_version: str
    model_name: str
    model_revision: str
    tokenizer_revision: str
    prompt_embedding_model: str
    prompt_embedding_revision: str
    prompt_embedding_license: str
    prompt_embedding_pooling_rule: str
    prompt_embedding_truncation_rule: str
    prompt_embedding_max_input_length: int
    chat_template: str
    chat_template_hash: str
    code_commit: str
    seed: int
    decoding: dict[str, Any]
    layer: Any
    token_position: Any
    stimulus_file_hash: str
    output_directory: str
    environment: str
    timestamp: str

    def validate(self, *, require_frozen_revision: bool = False) -> None:
        """Validate manifest completeness.

        With ``require_frozen_revision`` the model revision must not be a
        placeholder (enforced before any real data collection).
        """
        for name in (
            "experiment_id",
            "shard_id",
            "target_axis",
            "prompt_set_id",
            "prompt_set_version",
            "model_name",
            "model_revision",
            "tokenizer_revision",
            "prompt_embedding_model",
            "prompt_embedding_revision",
            "prompt_embedding_license",
            "prompt_embedding_pooling_rule",
            "prompt_embedding_truncation_rule",
            "chat_template",
            "chat_template_hash",
            "code_commit",
            "token_position",
            "stimulus_file_hash",
            "output_directory",
            "environment",
            "timestamp",
        ):
            _require_nonempty_str(getattr(self, name), f"manifest.{name}")
        if not isinstance(self.seed, int):
            raise ValidationError("manifest.seed must be an int")
        if not isinstance(self.decoding, dict):
            raise ValidationError("manifest.decoding must be a mapping")
        if (
            not isinstance(self.layer, int)
            or isinstance(self.layer, bool)
            or self.layer < 0
        ):
            raise ValidationError("manifest.layer must be a non-negative integer")
        if not isinstance(self.prompt_embedding_max_input_length, int) or isinstance(
            self.prompt_embedding_max_input_length, bool
        ):
            raise ValidationError(
                "manifest.prompt_embedding_max_input_length must be an int"
            )
        if self.run_kind not in RUN_KINDS:
            raise ValidationError(f"manifest.run_kind must be one of {RUN_KINDS}")
        if not isinstance(self.eligible_for_scientific_analysis, bool):
            raise ValidationError(
                "manifest.eligible_for_scientific_analysis must be a bool"
            )
        for name in SHA256_MANIFEST_FIELDS:
            value = getattr(self, name)
            if not is_sha256_field(value):
                raise ValidationError(
                    f"manifest.{name} must be an explicit sha256:<64 lowercase hex> "
                    f"digest, got {value!r}"
                )
        if self.run_kind == "technical_smoke":
            if self.eligible_for_scientific_analysis:
                raise ValidationError("technical smoke artifacts cannot be scientific")
            if not self.prompt_set_id.startswith("DISPOSABLE_"):
                raise ValidationError(
                    "technical smoke prompt_set_id must begin with DISPOSABLE_"
                )
            if "smoke" not in self.output_directory.lower():
                raise ValidationError(
                    "technical smoke output_directory must be visibly smoke-specific"
                )
            if self.shard_id.startswith("ASCR-Mini-"):
                raise ValidationError(
                    "technical smoke manifests cannot use a registered Mini shard id"
                )
            if self.prompt_embedding_max_input_length < 0:
                raise ValidationError(
                    "technical smoke prompt_embedding_max_input_length cannot be negative"
                )
        else:
            if not self.eligible_for_scientific_analysis:
                raise ValidationError(
                    "scientific feasibility manifests must declare scientific eligibility"
                )
            if self.prompt_set_id.startswith("DISPOSABLE_"):
                raise ValidationError(
                    "scientific feasibility cannot use a disposable smoke prompt set"
                )
            if not self.shard_id.startswith("ASCR-Mini-"):
                raise ValidationError(
                    "scientific feasibility requires a registered ASCR-Mini shard id"
                )
            if self.target_axis not in PRIMARY_AXES:
                raise ValidationError(
                    "scientific feasibility manifest.target_axis must be a registered "
                    f"primary axis, got {self.target_axis!r}"
                )
            if self.prompt_embedding_max_input_length <= 0:
                raise ValidationError(
                    "scientific feasibility requires a positive prompt-embedding "
                    "maximum input length"
                )
            for name in PROMPT_EMBEDDING_MANIFEST_FIELDS:
                if getattr(self, name) == NOT_APPLICABLE_TECHNICAL_SMOKE:
                    raise ValidationError(
                        f"manifest.{name} cannot be marked not-applicable in a "
                        "scientific feasibility run; the frozen prompt-embedding "
                        "comparator is mandatory"
                    )
        if require_frozen_revision:
            for name in (
                "model_revision",
                "tokenizer_revision",
                "prompt_embedding_model",
                "prompt_embedding_revision",
            ):
                value = getattr(self, name)
                if (
                    self.run_kind == "technical_smoke"
                    and name in (*PROMPT_EMBEDDING_MANIFEST_FIELDS,)
                    and value == NOT_APPLICABLE_TECHNICAL_SMOKE
                ):
                    # A technical smoke run may legitimately use no prompt-embedding
                    # model. It must say so explicitly rather than invent a frozen
                    # revision for a model it never loads.
                    continue
                if is_placeholder_revision(value):
                    raise ValidationError(
                        f"manifest.{name} is still a placeholder; freeze it before a run"
                    )
            if self.run_kind == "scientific_feasibility":
                for name in (
                    "experiment_id",
                    "prompt_set_id",
                    "prompt_set_version",
                    "prompt_embedding_model",
                    "prompt_embedding_license",
                    "prompt_embedding_pooling_rule",
                    "prompt_embedding_truncation_rule",
                    "chat_template",
                ):
                    value = getattr(self, name)
                    if _is_unfrozen_value(value):
                        raise ValidationError(
                            f"manifest.{name} is not frozen for a scientific run"
                        )
                for name in IMMUTABLE_REVISION_FIELDS:
                    value = getattr(self, name)
                    if not is_immutable_revision(value):
                        raise ValidationError(
                            f"manifest.{name} must be a full immutable hexadecimal "
                            "commit revision (40 lowercase hex characters) for a "
                            f"scientific run, got {value!r}"
                        )


def manifests_compatible(a: RunManifest, b: RunManifest) -> bool:
    """True if two shard manifests agree on all compatibility-relevant fields."""
    return all(getattr(a, name) == getattr(b, name) for name in _MANIFEST_COMPAT_FIELDS)


def _valid_layer_candidates(value: Any) -> bool:
    return (
        isinstance(value, (list, tuple))
        and bool(value)
        and all(
            isinstance(layer, int) and not isinstance(layer, bool) and layer >= 0
            for layer in value
        )
        and len(value) == len(set(value))
    )


def _valid_position_candidates(value: Any) -> bool:
    return (
        isinstance(value, (list, tuple))
        and bool(value)
        and all(
            isinstance(position, str)
            and bool(position.strip())
            and not position.startswith("TO_BE_")
            for position in value
        )
        and len(value) == len(set(value))
    )


@dataclass(frozen=True, slots=True)
class Mini0RunPlan:
    """Typed design-time view of the ASCR-Mini-0 pre-data run plan."""

    run_plan_version: str
    status: str
    validation_mode: str
    experiment_id: str
    shard_id: str
    run_kind: str
    eligible_for_scientific_analysis: bool
    target_axis: str
    prompt_set_id: str
    prompt_set_version: str
    stimulus_file_hash: str
    target_matched_groups: int
    model_name: str
    model_revision: str
    tokenizer_revision: str
    prompt_embedding_model: str
    prompt_embedding_revision: str
    prompt_embedding_selection_status: str
    prompt_embedding_license: str
    prompt_embedding_pooling_rule: str
    prompt_embedding_truncation_rule: str
    prompt_embedding_max_input_length: Any
    chat_template: str
    chat_template_hash: str
    code_commit: str
    layer_candidates: Any
    position_candidates: Any
    token_position: str
    h1_layer_position_status: Any
    h1_layer_position_raw_p_value_procedure: Any
    no_holonomy_data: bool
    remaining_mini0_author_decisions: tuple[str, ...]
    raw: dict[str, Any] = field(default_factory=dict, repr=False)


def parse_mini0_run_plan(data: dict[str, Any]) -> Mini0RunPlan:
    """Parse a draft or frozen Mini-0 plan without authorizing execution."""

    if not isinstance(data, dict):
        raise ValidationError("Mini-0 run-plan root must be a mapping")

    def text_field(name: str, default: str = "") -> str:
        value = data.get(name, default)
        if not isinstance(value, str):
            raise ValidationError(f"run plan {name} must be a string")
        return value

    fdr = data.get("fdr", {})
    h1_family = (
        fdr.get("h1_layer_position_sensitivity", {}) if isinstance(fdr, dict) else {}
    )
    if not isinstance(h1_family, dict):
        h1_family = {}
    decisions = data.get("remaining_mini0_author_decisions", ())
    if not isinstance(decisions, (list, tuple)):
        raise ValidationError("remaining_mini0_author_decisions must be a sequence")
    if any(not isinstance(decision, str) for decision in decisions):
        raise ValidationError(
            "remaining_mini0_author_decisions must contain only strings"
        )
    target_groups = data.get("target_matched_groups", 0)
    if not isinstance(target_groups, int) or isinstance(target_groups, bool):
        raise ValidationError("run plan target_matched_groups must be an int")
    return Mini0RunPlan(
        run_plan_version=text_field("run_plan_version"),
        status=text_field("status"),
        validation_mode=text_field("validation_mode", "draft"),
        experiment_id=text_field("experiment_id"),
        shard_id=text_field("shard_id"),
        run_kind=text_field("run_kind"),
        eligible_for_scientific_analysis=data.get(
            "eligible_for_scientific_analysis", False
        ),
        target_axis=text_field("target_axis"),
        prompt_set_id=text_field("prompt_set_id"),
        prompt_set_version=text_field("prompt_set_version"),
        stimulus_file_hash=text_field("stimulus_file_hash"),
        target_matched_groups=target_groups,
        model_name=text_field("model_name"),
        model_revision=text_field("model_revision"),
        tokenizer_revision=text_field("tokenizer_revision"),
        prompt_embedding_model=text_field("prompt_embedding_model"),
        prompt_embedding_revision=text_field("prompt_embedding_revision"),
        prompt_embedding_selection_status=text_field(
            "prompt_embedding_selection_status"
        ),
        prompt_embedding_license=text_field("prompt_embedding_license"),
        prompt_embedding_pooling_rule=text_field("prompt_embedding_pooling_rule"),
        prompt_embedding_truncation_rule=text_field("prompt_embedding_truncation_rule"),
        prompt_embedding_max_input_length=data.get("prompt_embedding_max_input_length"),
        chat_template=text_field("chat_template"),
        chat_template_hash=text_field("chat_template_hash"),
        code_commit=text_field("code_commit"),
        layer_candidates=data.get("layer_candidates"),
        position_candidates=data.get("position_candidates"),
        token_position=text_field("token_position"),
        h1_layer_position_status=h1_family.get("status"),
        h1_layer_position_raw_p_value_procedure=h1_family.get("raw_p_value_procedure"),
        no_holonomy_data=data.get("no_holonomy_data", False),
        remaining_mini0_author_decisions=tuple(decisions),
        raw=data,
    )


def load_mini0_run_plan(path: str | Path) -> Mini0RunPlan:
    """Load the Mini-0 YAML template without weakening its frozen gate."""

    import yaml

    with open(path, "r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    if not isinstance(data, dict):
        raise ValidationError("Mini-0 run-plan root must be a mapping")
    return parse_mini0_run_plan(data)


def run_plan_run_ready_problems(plan: Mini0RunPlan) -> list[str]:
    """Return every frozen-plan blocker for a scientific Mini-0 run."""

    problems: list[str] = []
    if plan.run_plan_version != "0.1.2":
        problems.append("run_plan_version must be 0.1.2")
    if plan.status != RUN_PLAN_FROZEN_STATUS:
        problems.append("Mini-0 run plan status is not FROZEN_PRE_DATA")
    if plan.validation_mode != "run_ready":
        problems.append("Mini-0 run plan validation_mode is not run_ready")
    if plan.shard_id != MINI0_SHARD_ID:
        problems.append(f"Mini-0 run plan shard_id must be {MINI0_SHARD_ID}")
    if plan.run_kind != "scientific_feasibility":
        problems.append("Mini-0 run plan run_kind must be scientific_feasibility")
    if plan.eligible_for_scientific_analysis is not True:
        problems.append("Mini-0 run plan must declare scientific eligibility")
    if plan.target_axis != MINI0_TARGET_AXIS:
        problems.append(f"Mini-0 target_axis must be {MINI0_TARGET_AXIS}")
    if plan.target_matched_groups < 40:
        problems.append("Mini-0 requires at least 40 complete matched groups")
    for label, value in (
        ("experiment_id", plan.experiment_id),
        ("prompt_set_id", plan.prompt_set_id),
        ("prompt_set_version", plan.prompt_set_version),
        ("model_name", plan.model_name),
        ("prompt_embedding_model", plan.prompt_embedding_model),
        ("prompt_embedding_license", plan.prompt_embedding_license),
        ("prompt_embedding_pooling_rule", plan.prompt_embedding_pooling_rule),
        ("prompt_embedding_truncation_rule", plan.prompt_embedding_truncation_rule),
        ("chat_template", plan.chat_template),
    ):
        if _is_unfrozen_value(value):
            problems.append(f"{label} is not frozen")
    for label, value in (
        ("model_revision", plan.model_revision),
        ("tokenizer_revision", plan.tokenizer_revision),
        ("prompt_embedding_revision", plan.prompt_embedding_revision),
        ("code_commit", plan.code_commit),
    ):
        if not is_immutable_revision(value):
            problems.append(
                f"{label} must be a full immutable 40-character lowercase hex revision"
            )
    if plan.prompt_embedding_selection_status != "AUTHOR_APPROVED_AND_FROZEN":
        problems.append("prompt-embedding selection is not author-approved and frozen")
    if (
        not isinstance(plan.prompt_embedding_max_input_length, int)
        or isinstance(plan.prompt_embedding_max_input_length, bool)
        or plan.prompt_embedding_max_input_length <= 0
    ):
        problems.append("prompt-embedding maximum input length must be a positive int")
    if not is_sha256_field(plan.stimulus_file_hash):
        problems.append("stimulus_file_hash must use sha256:<64 lowercase hex>")
    if not is_sha256_field(plan.chat_template_hash):
        problems.append("chat_template_hash must use sha256:<64 lowercase hex>")
    if not _valid_layer_candidates(plan.layer_candidates):
        problems.append(
            "layer_candidates must be a non-empty unique list of integers >= 0"
        )
    if not _valid_position_candidates(plan.position_candidates):
        problems.append("position_candidates must be a non-empty unique list of names")
    elif plan.token_position not in plan.position_candidates:
        problems.append("primary token_position must occur in position_candidates")
    if plan.h1_layer_position_status != RUN_PLAN_FROZEN_STATUS:
        problems.append("H1 layer/position sensitivity family is not FROZEN_PRE_DATA")
    if _is_unfrozen_value(
        plan.h1_layer_position_raw_p_value_procedure
    ) or not isinstance(plan.h1_layer_position_raw_p_value_procedure, dict):
        problems.append("H1 layer/position raw-p-value procedure is not frozen")
    if plan.no_holonomy_data is not True:
        problems.append("no_holonomy_data must be true")
    if plan.remaining_mini0_author_decisions:
        problems.append("Mini-0 still has unresolved author decisions")
    return problems


# ---------------------------------------------------------------------------
# Frozen statistical specification (v0.1.2 correction pass).
#
# These checks make the registered H1/H2 targets, estimands, sign conventions,
# decision rules, probe pipeline, selection objectives, seed roles, bootstrap
# algorithm, and BH procedure machine-enforced rather than prose-only. They read
# configuration text only; they compute no statistic and run no model.
# ---------------------------------------------------------------------------
def _require_mapping(value: Any, name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValidationError(f"{name} must be a mapping")
    return value


def _require_exact(value: Any, expected: Any, name: str) -> None:
    if value != expected:
        raise ValidationError(f"{name} must be {expected!r}, got {value!r}")


def validate_statistical_specification(data: dict[str, Any]) -> None:
    """Validate the frozen v0.1.2 H1/H2 statistical specification in a config.

    Raises :class:`ValidationError` if the registered target, estimand, sign
    convention, decision rules, probe pipeline, selection rule, seed roles,
    bootstrap algorithm, or BH procedure is missing or altered.
    """

    analysis = _require_mapping(data.get("analysis"), "analysis")

    h1 = _require_mapping(analysis.get("h1"), "analysis.h1")
    _require_exact(h1.get("target"), H1_TARGET, "analysis.h1.target")

    h2 = _require_mapping(analysis.get("h2"), "analysis.h2")
    _require_exact(h2.get("target"), H2_TARGET, "analysis.h2.target")
    if h2.get("target") == h1.get("target"):
        raise ValidationError(
            "H1 and H2 targets must stay distinct; H2 is not a second task-state "
            "classification test"
        )
    _require_exact(
        list(h2.get("target_classes") or []),
        list(STRATEGY_SUPERCLASSES),
        "analysis.h2.target_classes",
    )
    _require_exact(
        h2.get("primary_estimand"), H2_PRIMARY_ESTIMAND, "analysis.h2.primary_estimand"
    )
    _require_exact(
        h2.get("sign_convention"), H2_SIGN_CONVENTION, "analysis.h2.sign_convention"
    )
    _require_exact(
        h2.get("secondary_sign_convention"),
        H2_SECONDARY_SIGN_CONVENTION,
        "analysis.h2.secondary_sign_convention",
    )
    _require_exact(
        h2.get("fine_label_role"), "secondary", "analysis.h2.fine_label_role"
    )
    for rule in H2_DECISION_RULES:
        _require_nonempty_str(h2.get(rule), f"analysis.h2.{rule}")
    if h2.get("same_target_and_items_for_both_classifiers") is not True:
        raise ValidationError(
            "analysis.h2.same_target_and_items_for_both_classifiers must be true"
        )
    if h2.get("label_reliability_gate_blocks_inference") is not True:
        raise ValidationError(
            "analysis.h2.label_reliability_gate_blocks_inference must be true"
        )
    estimability = _require_mapping(h2.get("estimability"), "analysis.h2.estimability")
    _require_exact(
        estimability.get("single_class_training_fold"),
        NOT_ESTIMABLE,
        "analysis.h2.estimability.single_class_training_fold",
    )
    _require_exact(
        estimability.get("single_class_inner_fit_fold"),
        "affected_outer_fold_NOT_ESTIMABLE",
        "analysis.h2.estimability.single_class_inner_fit_fold",
    )
    _require_exact(
        estimability.get("single_class_final_outer_fit"),
        "affected_outer_fold_NOT_ESTIMABLE",
        "analysis.h2.estimability.single_class_final_outer_fit",
    )
    _require_exact(
        estimability.get("any_required_outer_fold_not_estimable_makes_aggregate"),
        "indeterminate",
        "analysis.h2.estimability.any_required_outer_fold_not_estimable_makes_aggregate",
    )
    _require_exact(
        estimability.get("not_estimable_primary_aggregate_is"),
        "indeterminate",
        "analysis.h2.estimability.not_estimable_primary_aggregate_is",
    )
    for flag in (
        "post_data_class_merging_forbidden",
        "post_data_fold_domain_direction_dropping_forbidden",
        "silent_exclusion_forbidden",
        "unconverged_models_may_not_score",
        "probability_columns_aligned_before_clipping",
    ):
        if estimability.get(flag) is not True:
            raise ValidationError(f"analysis.h2.estimability.{flag} must be true")
    _require_exact(
        list(estimability.get("evaluation_class_order") or []),
        list(STRATEGY_SUPERCLASSES),
        "analysis.h2.estimability.evaluation_class_order",
    )
    _require_exact(
        estimability.get("missing_training_class_probability"),
        0.0,
        "analysis.h2.estimability.missing_training_class_probability",
    )
    _require_exact(
        estimability.get("convergence_failure"),
        "candidate_invalid_then_outer_fold_NOT_ESTIMABLE_if_none_converges",
        "analysis.h2.estimability.convergence_failure",
    )
    clipping = _require_mapping(
        estimability.get("log_loss_probability_clipping"),
        "analysis.h2.estimability.log_loss_probability_clipping",
    )
    if not isinstance(clipping.get("epsilon"), float) or not (
        0.0 < float(clipping["epsilon"]) < 1.0
    ):
        raise ValidationError(
            "analysis.h2.estimability.log_loss_probability_clipping.epsilon must be "
            "a float strictly between 0 and 1"
        )
    _require_exact(
        clipping.get("dtype"),
        "float64",
        "analysis.h2.estimability.log_loss_probability_clipping.dtype",
    )
    if clipping.get("applied_identically_to_both_classifiers") is not True:
        raise ValidationError(
            "the log-loss clipping rule must apply identically to both classifiers"
        )

    pipeline = _require_mapping(
        analysis.get("probe_pipeline"), "analysis.probe_pipeline"
    )
    _require_exact(pipeline.get("penalty"), "l2", "analysis.probe_pipeline.penalty")
    _require_exact(pipeline.get("solver"), "lbfgs", "analysis.probe_pipeline.solver")
    _require_exact(
        pipeline.get("scaler_fit_scope"),
        "relevant_training_subset_only",
        "analysis.probe_pipeline.scaler_fit_scope",
    )
    _require_nonempty_str(pipeline.get("scaler"), "analysis.probe_pipeline.scaler")
    if pipeline.get("fit_intercept") is not True:
        raise ValidationError("analysis.probe_pipeline.fit_intercept must be true")
    if pipeline.get("class_weight") is not None:
        raise ValidationError("analysis.probe_pipeline.class_weight must be null")
    _require_exact(pipeline.get("max_iter"), 5000, "analysis.probe_pipeline.max_iter")
    if float(pipeline.get("tol", -1.0)) != 1e-6:
        raise ValidationError("analysis.probe_pipeline.tol must be 1e-6")
    _require_exact(pipeline.get("dtype"), "float64", "analysis.probe_pipeline.dtype")
    grid = [float(c) for c in (pipeline.get("regularization_grid_C") or [])]
    _require_exact(
        grid,
        list(REGULARIZATION_C_GRID),
        "analysis.probe_pipeline.regularization_grid_C",
    )
    if pipeline.get("grid_frozen_before_data") is not True:
        raise ValidationError(
            "analysis.probe_pipeline.grid_frozen_before_data must be true"
        )
    if pipeline.get("sparse_baselines_are_secondary") is not True:
        raise ValidationError(
            "sparse baselines must remain secondary and must not inherit dense "
            "centering silently"
        )

    selection = _require_mapping(
        analysis.get("hyperparameter_selection"), "analysis.hyperparameter_selection"
    )
    for key in (
        "h1_inner_objective",
        "h2_inner_objective",
        "first_tie_break",
        "second_tie_break_hidden_state",
    ):
        _require_nonempty_str(
            selection.get(key), f"analysis.hyperparameter_selection.{key}"
        )
    _require_exact(
        selection.get("first_tie_break"),
        "smaller_C_stronger_regularization",
        "analysis.hyperparameter_selection.first_tie_break",
    )
    _require_exact(
        selection.get("second_tie_break_hidden_state"),
        "earlier_layer_index",
        "analysis.hyperparameter_selection.second_tie_break_hidden_state",
    )
    tolerance = selection.get("numerical_tie_tolerance")
    if not isinstance(tolerance, float) or not (0.0 < tolerance < 1.0):
        raise ValidationError(
            "analysis.hyperparameter_selection.numerical_tie_tolerance must be a "
            "float strictly between 0 and 1"
        )
    _require_exact(
        selection.get("selection_scope"),
        "outer_training_domains_only",
        "analysis.hyperparameter_selection.selection_scope",
    )
    _require_exact(
        list(selection.get("h2_hidden_state_selects") or []),
        ["layer", "C"],
        "analysis.hyperparameter_selection.h2_hidden_state_selects",
    )
    _require_exact(
        list(selection.get("h2_prompt_embedding_selects") or []),
        ["C"],
        "analysis.hyperparameter_selection.h2_prompt_embedding_selects",
    )
    for flag in (
        "h2_classifiers_use_same_inner_folds_target_items_and_objective",
        "h2_classifiers_select_independently",
        "smaller_C_tie_break_applied_separately",
    ):
        if selection.get(flag) is not True:
            raise ValidationError(
                f"analysis.hyperparameter_selection.{flag} must be true"
            )
    _require_exact(
        selection.get("earlier_layer_tie_break_applies_to"),
        "hidden_state_only",
        "analysis.hyperparameter_selection.earlier_layer_tie_break_applies_to",
    )

    inner = _require_mapping(
        analysis.get("inner_validation"), "analysis.inner_validation"
    )
    _require_exact(
        inner.get("scheme"),
        "leave_one_training_domain_out",
        "analysis.inner_validation.scheme",
    )
    _require_exact(inner.get("folds"), 3, "analysis.inner_validation.folds")
    for flag in (
        "whole_matched_groups_disjoint",
        "concept_transfer_direction_crossed",
    ):
        if inner.get(flag) is not True:
            raise ValidationError(f"analysis.inner_validation.{flag} must be true")
    if inner.get("outer_test_domain_excluded") is not True:
        raise ValidationError(
            "analysis.inner_validation.outer_test_domain_excluded must be true"
        )

    _require_exact(analysis.get("primary_seed"), PRIMARY_SEED, "analysis.primary_seed")
    _require_exact(
        tuple(int(s) for s in (analysis.get("sensitivity_seeds") or ())),
        SENSITIVITY_SEEDS,
        "analysis.sensitivity_seeds",
    )
    _require_exact(
        tuple(int(s) for s in (analysis.get("seeds") or ())),
        (PRIMARY_SEED,) + SENSITIVITY_SEEDS,
        "analysis.seeds",
    )
    _require_exact(
        analysis.get("bootstrap_seed"), BOOTSTRAP_SEED, "analysis.bootstrap_seed"
    )
    _require_exact(
        analysis.get("permutation_seed"), PERMUTATION_SEED, "analysis.permutation_seed"
    )
    if analysis.get("pool_predictions_across_seeds") is not False:
        raise ValidationError(
            "analysis.pool_predictions_across_seeds must be false; only the primary "
            "seed produces the H1/H2 decision statistics"
        )
    if analysis.get("primary_decision_uses_primary_seed_only") is not True:
        raise ValidationError(
            "analysis.primary_decision_uses_primary_seed_only must be true"
        )
    if analysis.get("split_assignments_depend_on_seed") is not False:
        raise ValidationError(
            "outer and inner LODO assignments are deterministic and must not vary "
            "by seed"
        )

    bootstrap = _require_mapping(analysis.get("bootstrap"), "analysis.bootstrap")
    _require_exact(bootstrap.get("resamples"), 1000, "analysis.bootstrap.resamples")
    _require_exact(
        bootstrap.get("resampling_unit"),
        "complete_matched_group_cluster",
        "analysis.bootstrap.resampling_unit",
    )
    for flag in (
        "stratified_within_held_out_domain",
        "preserves_groups_contributed_per_domain",
        "group_predictions_travel_together",
    ):
        if bootstrap.get(flag) is not True:
            raise ValidationError(f"analysis.bootstrap.{flag} must be true")
    for flag in (
        "resample_items",
        "resample_cells",
        "resample_directions",
        "resample_seeds",
    ):
        if bootstrap.get(flag) is not False:
            raise ValidationError(
                f"analysis.bootstrap.{flag} must be false; only complete matched "
                "groups are resampled"
            )
    _require_exact(
        [float(x) for x in (bootstrap.get("interval_percentiles") or [])],
        [2.5, 97.5],
        "analysis.bootstrap.interval_percentiles",
    )
    _require_exact(
        bootstrap.get("interval_type"), "percentile", "analysis.bootstrap.interval_type"
    )
    _require_exact(
        bootstrap.get("h1_predictions_per_held_out_group"),
        4,
        "analysis.bootstrap.h1_predictions_per_held_out_group",
    )
    if bootstrap.get("h2_pairs_resampled_together") is not True:
        raise ValidationError(
            "analysis.bootstrap.h2_pairs_resampled_together must be true"
        )

    reliability = _require_mapping(
        analysis.get("response_label_reliability"),
        "analysis.response_label_reliability",
    )
    required_reliability_values = {
        "primary_labeler_scope": "all_generated_responses",
        "second_labeler": "independent_human",
        "subset_unit": "complete_matched_group",
        "subset_count_rule": "ceil_0.30_times_total_complete_groups",
        "selection_timing": "before_response_labels_are_observed",
        "stratification": "domain_as_evenly_as_possible",
        "taxonomy": "four_registered_response_strategy_superclasses",
        "reliability_timing": "before_adjudication",
        "primary_statistic": "cohen_kappa",
        "fewer_than_two_observed_classes": "NOT_ESTIMABLE_AND_FAIL",
        "failed_gate_action": "withhold_H2_and_H3_inference",
        "adjudication_timing": "after_pre_adjudication_reliability",
    }
    for key, expected in required_reliability_values.items():
        _require_exact(
            reliability.get(key),
            expected,
            f"analysis.response_label_reliability.{key}",
        )
    if float(reliability.get("subset_fraction", -1.0)) != (
        RESPONSE_LABEL_RELIABILITY_FRACTION
    ):
        raise ValidationError("response-label subset_fraction must be 0.30")
    _require_exact(
        reliability.get("subset_seed"),
        RESPONSE_LABEL_RELIABILITY_SEED,
        "analysis.response_label_reliability.subset_seed",
    )
    if float(reliability.get("pass_threshold_kappa", -1.0)) != (
        RESPONSE_LABEL_RELIABILITY_KAPPA_THRESHOLD
    ):
        raise ValidationError("response-label pass_threshold_kappa must be 0.60")
    _require_exact(
        reliability.get("bootstrap_seed"),
        RESPONSE_LABEL_RELIABILITY_BOOTSTRAP_SEED,
        "analysis.response_label_reliability.bootstrap_seed",
    )
    _require_exact(
        reliability.get("bootstrap_resamples"),
        1000,
        "analysis.response_label_reliability.bootstrap_resamples",
    )
    _require_exact(
        reliability.get("bootstrap_unit"),
        "complete_matched_group",
        "analysis.response_label_reliability.bootstrap_unit",
    )
    _require_exact(
        reliability.get("confidence_interval"),
        "95pct_matched_group_cluster_bootstrap",
        "analysis.response_label_reliability.confidence_interval",
    )
    required_reports = {
        "raw_agreement",
        "four_class_confusion_matrix",
        "class_counts_by_labeler",
        "cohen_kappa",
        "kappa_95pct_cluster_bootstrap_ci",
    }
    if set(reliability.get("required_reports") or []) != required_reports:
        raise ValidationError(
            "analysis.response_label_reliability.required_reports is incomplete"
        )
    for flag in (
        "second_labeler_blinded_to_primary_labels",
        "adjudicator_and_rule_recorded",
    ):
        if reliability.get(flag) is not True:
            raise ValidationError(
                f"analysis.response_label_reliability.{flag} must be true"
            )

    fdr = _require_mapping(data.get("fdr_families"), "fdr_families")
    procedure = _require_mapping(fdr.get("procedure"), "fdr_families.procedure")
    if float(procedure.get("q", -1.0)) != BH_Q:
        raise ValidationError(f"fdr_families.procedure.q must be {BH_Q}")
    _require_exact(
        procedure.get("method"), "benjamini_hochberg", "fdr_families.procedure.method"
    )
    _require_exact(
        procedure.get("operates_on"),
        "preregistered_one_sided_raw_p_values",
        "fdr_families.procedure.operates_on",
    )
    if procedure.get("confidence_intervals_are_fdr_corrected") is not False:
        raise ValidationError(
            "an ordinary confidence interval is never FDR-corrected; report raw "
            "effects and intervals separately from BH q-values"
        )
    if procedure.get("secondary_can_replace_primary") is not False:
        raise ValidationError(
            "fdr_families.procedure.secondary_can_replace_primary must be false"
        )
    for family in ("h1_direction_domain_secondary", "h2_direction_domain_secondary"):
        block = _require_mapping(fdr.get(family), f"fdr_families.{family}")
        raw_p = _require_mapping(
            block.get("raw_p_value_procedure"),
            f"fdr_families.{family}.raw_p_value_procedure",
        )
        _require_nonempty_str(
            raw_p.get("test"), f"fdr_families.{family}.raw_p_value_procedure.test"
        )
        _require_exact(
            raw_p.get("permutations"),
            10000,
            f"fdr_families.{family}.raw_p_value_procedure.permutations",
        )
        _require_exact(
            raw_p.get("seed"),
            PERMUTATION_SEED,
            f"fdr_families.{family}.raw_p_value_procedure.seed",
        )
        _require_exact(
            raw_p.get("null_unit"),
            "matched_group",
            f"fdr_families.{family}.raw_p_value_procedure.null_unit",
        )
        if raw_p.get("plus_one_correction") is not True:
            raise ValidationError(
                f"fdr_families.{family}.raw_p_value_procedure.plus_one_correction "
                "must be true"
            )
        _require_nonempty_str(
            raw_p.get("one_sided_direction"),
            f"fdr_families.{family}.raw_p_value_procedure.one_sided_direction",
        )

    family_test = _require_mapping(
        data.get("family_structure_test"), "family_structure_test"
    )
    if "decision_rule" in family_test:
        raise ValidationError(
            "family_structure_test.decision_rule is obsolete; use component-specific rules"
        )
    _require_exact(
        family_test.get("decision_logic"),
        "A_and_B_and_C",
        "family_structure_test.decision_logic",
    )
    component_rules = _require_mapping(
        family_test.get("component_rules"),
        "family_structure_test.component_rules",
    )
    expected_components = {
        "A_shared_vs_separate": "raw_95pct_ci_entirely_below_zero",
        "B_behavioral_specificity": "raw_95pct_ci_entirely_above_zero",
        "C_incremental": "raw_95pct_ci_entirely_above_zero",
    }
    if set(component_rules) != set(expected_components):
        raise ValidationError("family structure component rules must be exactly A/B/C")
    for component, interval_rule in expected_components.items():
        rule = _require_mapping(
            component_rules.get(component),
            f"family_structure_test.component_rules.{component}",
        )
        _require_exact(
            rule.get("raw_interval_condition"),
            interval_rule,
            f"family_structure_test.component_rules.{component}.raw_interval_condition",
        )
        _require_exact(
            rule.get("bh_condition"),
            "component_one_sided_raw_p_value_BH_adjusted_q_le_0.05",
            f"family_structure_test.component_rules.{component}.bh_condition",
        )


# ---------------------------------------------------------------------------
# Config loading.
# ---------------------------------------------------------------------------
@dataclass(frozen=True, slots=True)
class PilotConfig:
    """Minimal validated view of ``configs/pilot.yaml``."""

    config_version: str
    model_name: str
    model_revision: str
    tokenizer_revision: str
    replication_model: str | None
    prompt_embedding_model: str
    prompt_embedding_revision: str
    prompt_embedding_selection_status: str
    prompt_embedding_license: str
    prompt_embedding_pooling_rule: str
    prompt_embedding_truncation_rule: str
    prompt_embedding_max_input_length: Any
    study_stage: str
    run_gate_stage: str
    mini_shard_id: str
    target_axis: str
    axes: tuple[str, ...]
    domains: tuple[str, ...]
    layers: str
    seeds: tuple[int, ...]
    primary_seed: int | None
    sensitivity_seeds: tuple[int, ...]
    bootstrap_seed: int | None
    permutation_seed: int | None
    validation_mode: str
    run_kind: str
    eligible_for_scientific_analysis: bool
    target_matched_groups: int | None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @property
    def revision_is_frozen(self) -> bool:
        """True once the model revision is no longer a placeholder."""
        return not is_placeholder_revision(self.model_revision)

    @property
    def is_historical(self) -> bool:
        """Whether this is a readable historical v0.1.1 configuration."""

        return self.config_version == "0.1.1"


def parse_config(data: dict[str, Any]) -> PilotConfig:
    """Validate a config dict and return a :class:`PilotConfig`.

    Kept separate from file IO so it can be tested without a YAML dependency.
    """
    for key in ("config_version", "model", "design", "activations", "analysis"):
        if key not in data:
            raise ValidationError(f"config missing top-level section {key!r}")

    config_version = data["config_version"]
    _require_nonempty_str(str(config_version), "config_version")
    if str(config_version) not in SUPPORTED_CONFIG_VERSIONS:
        raise ValidationError(
            f"unsupported config_version {config_version!r}; "
            f"expected one of {SUPPORTED_CONFIG_VERSIONS}"
        )

    model = data["model"]
    model_name = model.get("name")
    model_revision = model.get("revision")
    _require_nonempty_str(model_name, "model.name")
    # The immutable revision hash must be recorded before data generation. Until
    # then it is intentionally the sentinel string below.
    _require_nonempty_str(model_revision, "model.revision")
    tokenizer_revision = model.get("tokenizer_revision", PLACEHOLDER_TOKENIZER_REVISION)
    _require_nonempty_str(tokenizer_revision, "model.tokenizer_revision")

    # Replication model (v0.1.1 amendment): must differ from the primary model once
    # an actual model is chosen; a placeholder is allowed until then.
    replication_model = model.get("replication_model")
    if replication_model is not None:
        _require_nonempty_str(replication_model, "model.replication_model")
        if (
            replication_model != PLACEHOLDER_REPLICATION_MODEL
            and replication_model == model_name
        ):
            raise ValidationError(
                "model.replication_model must differ from model.name once selected; "
                f"both are {model_name!r}"
            )

    embedding = data.get("prompt_embedding", {})
    prompt_embedding_model = embedding.get("model_name", PLACEHOLDER_EMBEDDING_MODEL)
    prompt_embedding_revision = embedding.get(
        "revision", PLACEHOLDER_EMBEDDING_REVISION
    )
    prompt_embedding_selection_status = embedding.get(
        "selection_status", "AUTHOR_APPROVAL_REQUIRED"
    )
    prompt_embedding_license = embedding.get(
        "license", "TO_BE_RECORDED_AFTER_AUTHOR_SELECTION"
    )
    prompt_embedding_pooling_rule = embedding.get(
        "pooling_rule", "TO_BE_FROZEN_AFTER_AUTHOR_SELECTION"
    )
    prompt_embedding_truncation_rule = str(
        embedding.get("truncation_rule", "TO_BE_FROZEN_AFTER_AUTHOR_SELECTION")
    )
    prompt_embedding_max_input_length = embedding.get(
        "max_input_length", "TO_BE_FROZEN_AFTER_AUTHOR_SELECTION"
    )
    _require_nonempty_str(prompt_embedding_model, "prompt_embedding.model_name")
    _require_nonempty_str(prompt_embedding_revision, "prompt_embedding.revision")
    _require_nonempty_str(
        prompt_embedding_selection_status, "prompt_embedding.selection_status"
    )
    _require_nonempty_str(prompt_embedding_license, "prompt_embedding.license")
    _require_nonempty_str(
        prompt_embedding_pooling_rule, "prompt_embedding.pooling_rule"
    )
    _require_nonempty_str(
        prompt_embedding_truncation_rule, "prompt_embedding.truncation_rule"
    )
    if isinstance(prompt_embedding_max_input_length, str):
        _require_nonempty_str(
            prompt_embedding_max_input_length, "prompt_embedding.max_input_length"
        )
    elif not isinstance(prompt_embedding_max_input_length, int) or isinstance(
        prompt_embedding_max_input_length, bool
    ):
        raise ValidationError(
            "prompt_embedding.max_input_length must be a positive int or draft sentinel"
        )

    design = data["design"]
    axes = tuple(design.get("axes", ()))
    domains = tuple(design.get("domains", ()))
    unknown_axes = [a for a in axes if a not in AXES]
    if unknown_axes:
        raise ValidationError(f"config references unknown axes: {unknown_axes}")
    unknown_domains = [d for d in domains if d not in DOMAINS]
    if unknown_domains:
        raise ValidationError(f"config references unknown domains: {unknown_domains}")
    study_stage = str(data.get("study_stage", "pre_data_feasibility_design"))
    run_gate_stage = str(data.get("run_gate_stage", MINI0_GATE_STAGE))
    if run_gate_stage not in RUN_GATE_STAGES:
        raise ValidationError(f"run_gate_stage must be one of {RUN_GATE_STAGES}")
    mini_shard_id = str(data.get("mini_shard_id", MINI0_SHARD_ID))
    target_axis = str(data.get("target_axis", axes[0] if len(axes) == 1 else ""))
    if target_axis and target_axis not in PRIMARY_AXES:
        raise ValidationError(
            f"target_axis must be one of {PRIMARY_AXES}, got {target_axis!r}"
        )

    activations = data["activations"]
    layers = str(activations.get("layers", "all"))

    analysis = data["analysis"]
    seeds = tuple(int(s) for s in analysis.get("seeds", ()))
    if not seeds:
        raise ValidationError("config analysis.seeds must be non-empty")
    primary_seed = analysis.get("primary_seed")
    if primary_seed is not None:
        if not isinstance(primary_seed, int) or isinstance(primary_seed, bool):
            raise ValidationError("analysis.primary_seed must be an int")
    sensitivity_seeds = tuple(int(s) for s in analysis.get("sensitivity_seeds", ()))
    bootstrap_seed = analysis.get("bootstrap_seed")
    permutation_seed = analysis.get("permutation_seed")
    for name, value in (
        ("analysis.bootstrap_seed", bootstrap_seed),
        ("analysis.permutation_seed", permutation_seed),
    ):
        if value is not None and (
            not isinstance(value, int) or isinstance(value, bool)
        ):
            raise ValidationError(f"{name} must be an int")

    # The frozen statistical specification is binding for v0.1.2 configurations.
    # Historical v0.1.1 configurations stay readable exactly as archived.
    if str(config_version) == "0.1.2":
        validate_statistical_specification(data)

    validation_mode = data.get("validation_mode", "draft")
    if validation_mode not in QA_MODES:
        raise ValidationError(f"validation_mode must be one of {QA_MODES}")
    run_kind = data.get("run_kind", "scientific_feasibility")
    if run_kind not in RUN_KINDS:
        raise ValidationError(f"run_kind must be one of {RUN_KINDS}")
    eligible = data.get("eligible_for_scientific_analysis", True)
    if not isinstance(eligible, bool):
        raise ValidationError("eligible_for_scientific_analysis must be bool")
    if run_kind == "technical_smoke" and eligible:
        raise ValidationError(
            "technical_smoke cannot be eligible for scientific analysis"
        )
    target = data.get("target_matched_groups")
    if target is not None and (
        not isinstance(target, int) or isinstance(target, bool) or target <= 0
    ):
        raise ValidationError("target_matched_groups must be a positive integer")

    return PilotConfig(
        config_version=str(config_version),
        model_name=model_name,
        model_revision=model_revision,
        tokenizer_revision=tokenizer_revision,
        replication_model=replication_model,
        prompt_embedding_model=prompt_embedding_model,
        prompt_embedding_revision=prompt_embedding_revision,
        prompt_embedding_selection_status=prompt_embedding_selection_status,
        prompt_embedding_license=prompt_embedding_license,
        prompt_embedding_pooling_rule=prompt_embedding_pooling_rule,
        prompt_embedding_truncation_rule=prompt_embedding_truncation_rule,
        prompt_embedding_max_input_length=prompt_embedding_max_input_length,
        study_stage=study_stage,
        run_gate_stage=run_gate_stage,
        mini_shard_id=mini_shard_id,
        target_axis=target_axis,
        axes=axes,
        domains=domains,
        layers=layers,
        seeds=seeds,
        primary_seed=primary_seed,
        sensitivity_seeds=sensitivity_seeds,
        bootstrap_seed=bootstrap_seed,
        permutation_seed=permutation_seed,
        validation_mode=validation_mode,
        run_kind=run_kind,
        eligible_for_scientific_analysis=eligible,
        target_matched_groups=target,
        raw=data,
    )


def config_run_ready_problems(
    config: PilotConfig, *, stage: str | None = None
) -> list[str]:
    """Return stage-aware v0.1.2 configuration blockers without model work."""

    problems: list[str] = []
    gate_stage = stage or config.run_gate_stage
    if gate_stage not in RUN_GATE_STAGES:
        problems.append(f"unknown run gate stage {gate_stage!r}")
    if config.is_historical:
        problems.append(
            "historical v0.1.1 config is readable but cannot be v0.1.2 run_ready"
        )
    if config.validation_mode != "run_ready":
        problems.append(
            "validation_mode is draft; scientific data generation is blocked"
        )
    for label, value in (
        ("prompt-embedding model", config.prompt_embedding_model),
        ("prompt-embedding license", config.prompt_embedding_license),
        ("prompt-embedding pooling rule", config.prompt_embedding_pooling_rule),
        ("prompt-embedding truncation rule", config.prompt_embedding_truncation_rule),
    ):
        if _is_unfrozen_value(value):
            problems.append(f"{label} is still a placeholder or empty")
    for label, value in (
        ("model revision", config.model_revision),
        ("tokenizer revision", config.tokenizer_revision),
        ("prompt-embedding revision", config.prompt_embedding_revision),
    ):
        if not is_immutable_revision(value):
            problems.append(
                f"{label} must be a full immutable 40-character lowercase hex revision"
            )
    if (
        not isinstance(config.prompt_embedding_max_input_length, int)
        or isinstance(config.prompt_embedding_max_input_length, bool)
        or config.prompt_embedding_max_input_length <= 0
    ):
        problems.append("prompt-embedding maximum input length must be a positive int")
    if config.prompt_embedding_selection_status != "AUTHOR_APPROVED_AND_FROZEN":
        problems.append("prompt-embedding selection still requires author approval")
    if config.mini_shard_id != MINI0_SHARD_ID and gate_stage == MINI0_GATE_STAGE:
        problems.append(f"Mini-0 config mini_shard_id must be {MINI0_SHARD_ID}")
    if config.target_axis != MINI0_TARGET_AXIS and gate_stage == MINI0_GATE_STAGE:
        problems.append(f"Mini-0 config target_axis must be {MINI0_TARGET_AXIS}")
    if config.target_axis not in config.axes:
        problems.append("target_axis must be included in design.axes")
    if config.domains != DOMAINS:
        problems.append(
            "design.domains must contain all four registered domains in order"
        )
    if config.target_matched_groups is None:
        problems.append("target matched-group count is missing")
    elif gate_stage == MINI0_GATE_STAGE and config.target_matched_groups < 40:
        problems.append("Mini-0 target matched-group count must be at least 40")
    if config.raw.get("no_holonomy_data") is not True:
        problems.append("no_holonomy_data must be true for every ASCR shard")
    activations = config.raw.get("activations", {})
    layer_candidates = activations.get("primary_layer_candidates")
    if not _valid_layer_candidates(layer_candidates):
        problems.append(
            "primary layer candidate grid must be a non-empty unique list of integers >= 0"
        )
    position_candidates = activations.get("primary_position_candidates")
    if not _valid_position_candidates(position_candidates):
        problems.append(
            "primary position candidate grid must be a non-empty unique list of names"
        )
    h1_block = config.raw.get("fdr_families", {}).get(
        "h1_layer_position_sensitivity", {}
    )
    h1_layer_family = h1_block.get("status") if isinstance(h1_block, dict) else None
    if h1_layer_family != RUN_PLAN_FROZEN_STATUS:
        problems.append("H1 layer/position FDR family is not frozen")
    h1_raw_p = (
        h1_block.get("raw_p_value_procedure") if isinstance(h1_block, dict) else None
    )
    if not isinstance(h1_raw_p, dict) or _is_unfrozen_value(h1_raw_p):
        problems.append("H1 layer/position raw-p-value procedure is not frozen")
    if gate_stage == H3_GATE_STAGE:
        problems.extend(h3_run_ready_problems(config))
    if config.run_kind == "technical_smoke":
        if config.eligible_for_scientific_analysis:
            problems.append("technical smoke configuration cannot be scientific")
    elif not config.eligible_for_scientific_analysis:
        problems.append(
            "scientific feasibility config must declare scientific eligibility"
        )
    return problems


def h3_run_ready_problems(config: PilotConfig) -> list[str]:
    """Return only the later H3 intervention-family blockers."""

    h3 = config.raw.get("fdr_families", {}).get("h3_intervention", {})
    if not isinstance(h3, dict):
        return ["H3 intervention FDR family is missing"]
    problems: list[str] = []
    if h3.get("status") != RUN_PLAN_FROZEN_STATUS:
        problems.append("H3 intervention FDR family is not frozen")
    if not isinstance(h3.get("raw_p_value_procedure"), dict) or _is_unfrozen_value(
        h3.get("raw_p_value_procedure")
    ):
        problems.append("H3 intervention raw-p-value procedure is not frozen")
    intervention = config.raw.get("intervention", {})
    if not isinstance(intervention, dict):
        problems.append("H3 intervention grid is missing")
    else:
        for key in ("strengths", "layers"):
            if _is_unfrozen_value(intervention.get(key)):
                problems.append(f"H3 intervention {key} grid is not frozen")
    return problems


def config_can_generate_scientific_data(config: PilotConfig) -> bool:
    """Always false: a configuration alone cannot authorize a scientific run.

    Retained as a fail-closed compatibility helper. Scientific authorization needs
    the config, frozen run plan, immutable manifest, and validated stimulus set via
    :func:`scientific_run_authorized`.
    """

    del config
    return False


def integrated_pre_run_gate_problems(
    config: PilotConfig,
    items: list[PromptItem],
    *,
    run_plan: Mini0RunPlan | None = None,
    manifest: RunManifest | None = None,
) -> list[str]:
    """Return every blocker that must be empty before a scientific run may start.

    This is the single authoritative Mini-0 gate. Configuration-only and
    stimulus-only helpers can diagnose their own inputs but cannot authorize model
    construction. A future runner must supply all four artifacts and find this list
    empty before constructing, downloading, or loading any model.
    """

    problems = [
        f"config: {p}"
        for p in config_run_ready_problems(config, stage=MINI0_GATE_STAGE)
    ]
    if run_plan is None:
        problems.append("run_plan: frozen Mini-0 run plan is missing")
    else:
        problems.extend(f"run_plan: {p}" for p in run_plan_run_ready_problems(run_plan))
    if manifest is None:
        problems.append("manifest: immutable scientific run manifest is missing")
    else:
        try:
            manifest.validate(require_frozen_revision=True)
        except ValidationError as exc:
            problems.append(f"manifest: {exc}")
    problems.extend(
        f"stimuli: {p}"
        for p in check_run_ready(
            items,
            model_revision=config.model_revision,
            tokenizer_revision=config.tokenizer_revision,
            prompt_embedding_model=config.prompt_embedding_model,
            prompt_embedding_revision=config.prompt_embedding_revision,
            min_complete_groups=config.target_matched_groups,
            target_axis=config.target_axis or MINI0_TARGET_AXIS,
            required_domains=DOMAINS,
            require_balanced_domains=True,
        )
    )
    if config.run_kind != "scientific_feasibility":
        problems.append(
            "run_kind is not scientific_feasibility; this gate authorizes no "
            "scientific extraction"
        )
    if run_plan is not None:
        config_activations = config.raw.get("activations", {})
        if not isinstance(config_activations, dict):
            config_activations = {}
        config_fdr = config.raw.get("fdr_families", {})
        if not isinstance(config_fdr, dict):
            config_fdr = {}
        config_h1_family = config_fdr.get("h1_layer_position_sensitivity", {})
        if not isinstance(config_h1_family, dict):
            config_h1_family = {}
        config_plan_pairs = (
            ("mini_shard_id", config.mini_shard_id, run_plan.shard_id),
            ("target_axis", config.target_axis, run_plan.target_axis),
            (
                "target_matched_groups",
                config.target_matched_groups,
                run_plan.target_matched_groups,
            ),
            ("model_name", config.model_name, run_plan.model_name),
            ("model_revision", config.model_revision, run_plan.model_revision),
            (
                "tokenizer_revision",
                config.tokenizer_revision,
                run_plan.tokenizer_revision,
            ),
            (
                "prompt_embedding_model",
                config.prompt_embedding_model,
                run_plan.prompt_embedding_model,
            ),
            (
                "prompt_embedding_revision",
                config.prompt_embedding_revision,
                run_plan.prompt_embedding_revision,
            ),
            (
                "prompt_embedding_selection_status",
                config.prompt_embedding_selection_status,
                run_plan.prompt_embedding_selection_status,
            ),
            (
                "prompt_embedding_license",
                config.prompt_embedding_license,
                run_plan.prompt_embedding_license,
            ),
            (
                "prompt_embedding_pooling_rule",
                config.prompt_embedding_pooling_rule,
                run_plan.prompt_embedding_pooling_rule,
            ),
            (
                "prompt_embedding_truncation_rule",
                config.prompt_embedding_truncation_rule,
                run_plan.prompt_embedding_truncation_rule,
            ),
            (
                "prompt_embedding_max_input_length",
                config.prompt_embedding_max_input_length,
                run_plan.prompt_embedding_max_input_length,
            ),
            (
                "layer_candidates",
                config_activations.get("primary_layer_candidates"),
                run_plan.layer_candidates,
            ),
            (
                "position_candidates",
                config_activations.get("primary_position_candidates"),
                run_plan.position_candidates,
            ),
            (
                "h1_layer_position_status",
                config_h1_family.get("status"),
                run_plan.h1_layer_position_status,
            ),
            (
                "h1_layer_position_raw_p_value_procedure",
                config_h1_family.get("raw_p_value_procedure"),
                run_plan.h1_layer_position_raw_p_value_procedure,
            ),
        )
        for label, config_value, plan_value in config_plan_pairs:
            if config_value != plan_value:
                problems.append(f"compatibility: config/run-plan mismatch for {label}")
        canonical_hash = canonical_stimulus_hash(items)
        if run_plan.stimulus_file_hash != canonical_hash:
            problems.append(
                "compatibility: run-plan stimulus hash does not match canonical items"
            )
    if run_plan is not None and manifest is not None:
        plan_manifest_pairs = (
            ("experiment_id", run_plan.experiment_id, manifest.experiment_id),
            ("shard_id", run_plan.shard_id, manifest.shard_id),
            ("run_kind", run_plan.run_kind, manifest.run_kind),
            (
                "eligible_for_scientific_analysis",
                run_plan.eligible_for_scientific_analysis,
                manifest.eligible_for_scientific_analysis,
            ),
            ("target_axis", run_plan.target_axis, manifest.target_axis),
            ("prompt_set_id", run_plan.prompt_set_id, manifest.prompt_set_id),
            (
                "prompt_set_version",
                run_plan.prompt_set_version,
                manifest.prompt_set_version,
            ),
            (
                "stimulus_file_hash",
                run_plan.stimulus_file_hash,
                manifest.stimulus_file_hash,
            ),
            ("model_name", run_plan.model_name, manifest.model_name),
            ("model_revision", run_plan.model_revision, manifest.model_revision),
            (
                "tokenizer_revision",
                run_plan.tokenizer_revision,
                manifest.tokenizer_revision,
            ),
            (
                "prompt_embedding_model",
                run_plan.prompt_embedding_model,
                manifest.prompt_embedding_model,
            ),
            (
                "prompt_embedding_revision",
                run_plan.prompt_embedding_revision,
                manifest.prompt_embedding_revision,
            ),
            (
                "prompt_embedding_license",
                run_plan.prompt_embedding_license,
                manifest.prompt_embedding_license,
            ),
            (
                "prompt_embedding_pooling_rule",
                run_plan.prompt_embedding_pooling_rule,
                manifest.prompt_embedding_pooling_rule,
            ),
            (
                "prompt_embedding_truncation_rule",
                run_plan.prompt_embedding_truncation_rule,
                manifest.prompt_embedding_truncation_rule,
            ),
            (
                "prompt_embedding_max_input_length",
                run_plan.prompt_embedding_max_input_length,
                manifest.prompt_embedding_max_input_length,
            ),
            ("chat_template", run_plan.chat_template, manifest.chat_template),
            (
                "chat_template_hash",
                run_plan.chat_template_hash,
                manifest.chat_template_hash,
            ),
            ("code_commit", run_plan.code_commit, manifest.code_commit),
            ("token_position", run_plan.token_position, manifest.token_position),
        )
        for label, plan_value, manifest_value in plan_manifest_pairs:
            if plan_value != manifest_value:
                problems.append(
                    f"compatibility: run-plan/manifest mismatch for {label}"
                )
        if _valid_layer_candidates(run_plan.layer_candidates) and (
            manifest.layer not in run_plan.layer_candidates
        ):
            problems.append("compatibility: manifest layer is outside the frozen grid")
        if manifest.decoding != config.raw.get("model", {}).get("decoding"):
            problems.append("compatibility: manifest decoding differs from config")
    return problems


def scientific_run_authorized(
    config: PilotConfig,
    items: list[PromptItem],
    *,
    run_plan: Mini0RunPlan | None = None,
    manifest: RunManifest | None = None,
) -> bool:
    """True only when the integrated pre-run gate reports no blocker at all.

    A ``False`` result means no model may be constructed or loaded. This function
    never loads a model and never produces data.
    """

    return not integrated_pre_run_gate_problems(
        config,
        items,
        run_plan=run_plan,
        manifest=manifest,
    )


def load_config(path: str | Path) -> PilotConfig:
    """Load and validate ``pilot.yaml`` (requires PyYAML)."""
    import yaml  # local import keeps the package importable without PyYAML

    with open(path, "r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    if not isinstance(data, dict):
        raise ValidationError(f"config root must be a mapping, got {type(data)}")
    return parse_config(data)
