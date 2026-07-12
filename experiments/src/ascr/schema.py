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

# --- Concept-mention / naturalness QA schema (v0.1.1 amendment, 2nd pass) ---
#
# Two validation modes: "draft" (incomplete QA allowed; NO activation extraction)
# and "run_ready" (complete, typed QA required before any real run).
QA_MODES: tuple[str, ...] = ("draft", "run_ready")

# Boolean QA flags that must all be True for an item to pass.
QA_BOOLEAN_FIELDS: tuple[str, ...] = (
    "grammatical",
    "register_match",
    "domain_match",
    "target_task_match",
    "solvable_as_intended",
    "task_state_present_confirmed",
    "concept_mention_confirmed",
    "label_leak_free",
    "no_artificial_meta_sentence",
    "primary_axis_isolated",
)
QA_DISPOSITIONS: tuple[str, ...] = ("pass", "revise", "discard")
QA_MIN_NATURALNESS = 4
QA_MAX_GROUP_NATURALNESS_SPREAD = 1

# All fields a run_ready QA record must contain.
REQUIRED_QA_FIELDS: tuple[str, ...] = (
    ("naturalness_rating",)
    + QA_BOOLEAN_FIELDS
    + ("reviewer_id", "review_timestamp", "disposition")
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
    if not isinstance(rating, int) or isinstance(rating, bool) or not (1 <= rating <= 5):
        raise ValidationError(
            f"{item_id}: naturalness_rating must be an int in 1..5, got {rating!r}"
        )
    for name in QA_BOOLEAN_FIELDS:
        if not isinstance(qa[name], bool):
            raise ValidationError(f"{item_id}: qa.{name} must be a bool")
    _require_nonempty_str(qa["reviewer_id"], f"{item_id}: qa.reviewer_id")
    if not _is_iso8601(qa["review_timestamp"]):
        raise ValidationError(
            f"{item_id}: qa.review_timestamp must be an ISO-8601 string"
        )
    if qa["disposition"] not in QA_DISPOSITIONS:
        raise ValidationError(
            f"{item_id}: qa.disposition must be one of {QA_DISPOSITIONS}"
        )


def qa_item_passes(qa: dict[str, Any]) -> bool:
    """True if a *typed, run_ready-valid* QA record meets the pass criteria."""
    try:
        validate_qa(qa, mode="run_ready")
    except ValidationError:
        return False
    if qa["disposition"] != "pass":
        return False
    if any(qa[name] is not True for name in QA_BOOLEAN_FIELDS):
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
            if not qa_item_passes(self.qa):
                raise ValidationError(
                    f"{self.item_id}: QA does not pass (disposition/flags/naturalness)"
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
# Run-ready gate (v0.1.1 amendment, 2nd pass). NO run may proceed unless the whole
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


def check_run_ready(
    items: list[PromptItem],
    *,
    model_revision: str | None = None,
    min_complete_groups: int | None = None,
) -> list[str]:
    """Return a list of run-readiness problems (empty list == run_ready).

    A CLI-validatable routine over a whole stimulus set. It blocks a run when: any
    matched group is not run_ready; the model revision is still a placeholder; the
    number of complete run_ready groups is below the configured sample size; or an
    external item has not been review-approved.
    """
    problems: list[str] = []
    groups: dict[str, list[PromptItem]] = {}
    for item in items:
        groups.setdefault(item.matched_group_id, []).append(item)

    complete = 0
    for gid, gitems in sorted(groups.items()):
        try:
            validate_run_ready_group(gitems)
            complete += 1
        except ValidationError as exc:
            problems.append(f"group {gid}: {exc}")

    if model_revision is not None and is_placeholder_revision(model_revision):
        problems.append(
            "model revision is still a placeholder; freeze the immutable hash "
            "before any run"
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
    return problems


def is_run_ready(
    items: list[PromptItem],
    *,
    model_revision: str | None = None,
    min_complete_groups: int | None = None,
) -> bool:
    """True if the whole stimulus set passes the run-ready gate."""
    return not check_run_ready(
        items,
        model_revision=model_revision,
        min_complete_groups=min_complete_groups,
    )


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
