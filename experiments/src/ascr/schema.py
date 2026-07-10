"""Typed schema and validation for ASCR pilot prompt items.

This scaffold does *not* run the model experiment. It defines the metadata every
prompt item must carry so that the 2x2 design (actual task state x appraisal
concept mention) is well formed and machine-checkable before any activations are
extracted.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .strategy_labels import (
    AXES,
    DOMAINS,
    RESPONSE_STRATEGIES,
    design_cell,
)


class ValidationError(ValueError):
    """Raised when a prompt item or config fails schema validation."""


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

    @property
    def cell(self) -> str:
        """The design-cell label derived from the two design factors."""
        return design_cell(self.task_state_present, self.concept_mention_present)

    def validate(self) -> None:
        """Raise :class:`ValidationError` if any required metadata is invalid."""
        _require_nonempty_str(self.item_id, "item_id")
        _require_nonempty_str(self.prompt_text, "prompt_text")
        _require_nonempty_str(self.matched_group_id, "matched_group_id")

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
    allowed = {
        "item_id",
        "axis",
        "domain",
        "task_state_present",
        "concept_mention_present",
        "prompt_text",
        "matched_group_id",
        "expected_strategy_space",
        "notes",
    }
    unknown_keys = set(data) - allowed
    if unknown_keys:
        raise ValidationError(f"unknown item fields: {sorted(unknown_keys)}")
    missing = allowed - {"notes"} - set(data)
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
    )
    item.validate()
    return item


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


# ---------------------------------------------------------------------------
# Config loading.
# ---------------------------------------------------------------------------
@dataclass(frozen=True, slots=True)
class PilotConfig:
    """Minimal validated view of ``configs/pilot.yaml``."""

    model_name: str
    model_revision: str
    axes: tuple[str, ...]
    domains: tuple[str, ...]
    layers: str
    seeds: tuple[int, ...]
    raw: dict[str, Any] = field(default_factory=dict, repr=False)


def parse_config(data: dict[str, Any]) -> PilotConfig:
    """Validate a config dict and return a :class:`PilotConfig`.

    Kept separate from file IO so it can be tested without a YAML dependency.
    """
    for key in ("model", "design", "activations", "analysis"):
        if key not in data:
            raise ValidationError(f"config missing top-level section {key!r}")

    model = data["model"]
    model_name = model.get("name")
    model_revision = model.get("revision")
    _require_nonempty_str(model_name, "model.name")
    # The immutable revision hash must be recorded before data generation. Until
    # then it is intentionally the sentinel string below.
    _require_nonempty_str(model_revision, "model.revision")

    design = data["design"]
    axes = tuple(design.get("axes", ()))
    domains = tuple(design.get("domains", ()))
    unknown_axes = [a for a in axes if a not in AXES]
    if unknown_axes:
        raise ValidationError(f"config references unknown axes: {unknown_axes}")
    unknown_domains = [d for d in domains if d not in DOMAINS]
    if unknown_domains:
        raise ValidationError(f"config references unknown domains: {unknown_domains}")

    activations = data["activations"]
    layers = str(activations.get("layers", "all"))

    analysis = data["analysis"]
    seeds = tuple(int(s) for s in analysis.get("seeds", ()))
    if not seeds:
        raise ValidationError("config analysis.seeds must be non-empty")

    return PilotConfig(
        model_name=model_name,
        model_revision=model_revision,
        axes=axes,
        domains=domains,
        layers=layers,
        seeds=seeds,
        raw=data,
    )


def load_config(path: str | Path) -> PilotConfig:
    """Load and validate ``pilot.yaml`` (requires PyYAML)."""
    import yaml  # local import keeps the package importable without PyYAML

    with open(path, "r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    if not isinstance(data, dict):
        raise ValidationError(f"config root must be a mapping, got {type(data)}")
    return parse_config(data)
