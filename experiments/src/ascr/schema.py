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


# Sentinels that must be replaced before the first data collection / replication.
PLACEHOLDER_MODEL_REVISION = "TO_BE_FROZEN_BEFORE_DATA_GENERATION"
PLACEHOLDER_REPLICATION_MODEL = "TO_BE_SELECTED_BEFORE_CONFIRMATORY_REPLICATION"

# Required concept-mention / naturalness QA fields (v0.1.1 amendment). Present only
# after a matched group passes the stimulus-QA protocol; see
# preregistration/experimental-design.md.
REQUIRED_QA_FIELDS: tuple[str, ...] = (
    "naturalness",
    "grammatical",
    "register",
    "prompt_length",
    "syntactic_complexity",
    "domain_match",
    "target_task",
    "solvable",
    "task_state_present_confirmed",
    "concept_mention_confirmed",
    "label_leak_free",
    "no_meta_sentence",
)


def is_placeholder_revision(revision: str) -> bool:
    """True if ``revision`` is still an unfilled placeholder (not a frozen hash)."""
    return revision == PLACEHOLDER_MODEL_REVISION or revision.startswith("TO_BE_")


def validate_qa(qa: dict[str, Any], item_id: str = "<item>") -> None:
    """Validate a concept-mention/naturalness QA record."""
    if not isinstance(qa, dict):
        raise ValidationError(f"{item_id}: qa must be a mapping")
    missing = [k for k in REQUIRED_QA_FIELDS if k not in qa]
    if missing:
        raise ValidationError(f"{item_id}: qa missing required fields {missing}")


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
    qa: dict[str, Any] | None = None

    @property
    def cell(self) -> str:
        """The design-cell label derived from the two design factors."""
        return design_cell(self.task_state_present, self.concept_mention_present)

    def validate(self) -> None:
        """Raise :class:`ValidationError` if any required metadata is invalid."""
        _require_nonempty_str(self.item_id, "item_id")
        _require_nonempty_str(self.prompt_text, "prompt_text")
        _require_nonempty_str(self.matched_group_id, "matched_group_id")
        if self.qa is not None:
            validate_qa(self.qa, self.item_id)

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
    optional = {"notes", "qa"}
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
# Mini-shard run manifests (v0.1.1 amendment).
# ---------------------------------------------------------------------------
# Fields that must be identical for two shards to be safely combined.
_MANIFEST_COMPAT_FIELDS: tuple[str, ...] = (
    "prompt_set_version",
    "model_name",
    "model_revision",
    "tokenizer_revision",
    "chat_template",
    "code_commit",
    "decoding",
    "layer",
    "token_position",
    "environment",
)


@dataclass(frozen=True, slots=True)
class RunManifest:
    """Immutable manifest recorded for one mini-shard run.

    No run is executed here; this only fixes which fields must be captured and
    which must match for shards to be combinable.
    """

    experiment_id: str
    shard_id: str
    prompt_set_version: str
    model_name: str
    model_revision: str
    tokenizer_revision: str
    chat_template: str
    code_commit: str
    seed: int
    decoding: dict[str, Any]
    layer: Any
    token_position: Any
    stimulus_file_hash: str
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
            "prompt_set_version",
            "model_name",
            "model_revision",
            "tokenizer_revision",
            "chat_template",
            "code_commit",
            "stimulus_file_hash",
            "environment",
            "timestamp",
        ):
            _require_nonempty_str(getattr(self, name), f"manifest.{name}")
        if not isinstance(self.seed, int):
            raise ValidationError("manifest.seed must be an int")
        if not isinstance(self.decoding, dict):
            raise ValidationError("manifest.decoding must be a mapping")
        if require_frozen_revision and is_placeholder_revision(self.model_revision):
            raise ValidationError(
                "manifest.model_revision is still a placeholder; freeze the "
                "immutable revision hash before data collection"
            )


def manifests_compatible(a: RunManifest, b: RunManifest) -> bool:
    """True if two shard manifests agree on all compatibility-relevant fields."""
    return all(
        getattr(a, name) == getattr(b, name) for name in _MANIFEST_COMPAT_FIELDS
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
    replication_model: str | None
    axes: tuple[str, ...]
    domains: tuple[str, ...]
    layers: str
    seeds: tuple[int, ...]
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @property
    def revision_is_frozen(self) -> bool:
        """True once the model revision is no longer a placeholder."""
        return not is_placeholder_revision(self.model_revision)


def parse_config(data: dict[str, Any]) -> PilotConfig:
    """Validate a config dict and return a :class:`PilotConfig`.

    Kept separate from file IO so it can be tested without a YAML dependency.
    """
    for key in ("config_version", "model", "design", "activations", "analysis"):
        if key not in data:
            raise ValidationError(f"config missing top-level section {key!r}")

    config_version = data["config_version"]
    _require_nonempty_str(str(config_version), "config_version")

    model = data["model"]
    model_name = model.get("name")
    model_revision = model.get("revision")
    _require_nonempty_str(model_name, "model.name")
    # The immutable revision hash must be recorded before data generation. Until
    # then it is intentionally the sentinel string below.
    _require_nonempty_str(model_revision, "model.revision")

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
        config_version=str(config_version),
        model_name=model_name,
        model_revision=model_revision,
        replication_model=replication_model,
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
