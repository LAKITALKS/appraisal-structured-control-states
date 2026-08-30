"""Design-time split planners for the ASCR v0.1.2 H1 analysis.

The functions in this module operate only on prompt metadata. They do not load a
model, activations, outputs, or scientific observations. Their purpose is to make
the double-crossed leave-one-domain-out boundary mechanically inspectable before
data collection.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

from .schema import PromptItem, ValidationError, is_complete_matched_group
from .strategy_labels import DOMAINS

CONCEPT_ABSENT_TO_PRESENT: Final[str] = "concept_absent_to_present"
CONCEPT_PRESENT_TO_ABSENT: Final[str] = "concept_present_to_absent"
TRANSFER_DIRECTIONS: Final[tuple[str, ...]] = (
    CONCEPT_ABSENT_TO_PRESENT,
    CONCEPT_PRESENT_TO_ABSENT,
)

_SOURCE_CELLS: Final[dict[str, tuple[str, ...]]] = {
    CONCEPT_ABSENT_TO_PRESENT: (
        "A_neutral_control",
        "C_pure_task_induction",
    ),
    CONCEPT_PRESENT_TO_ABSENT: (
        "B_concept_tracking_only",
        "D_combined",
    ),
}
_TARGET_CELLS: Final[dict[str, tuple[str, ...]]] = {
    CONCEPT_ABSENT_TO_PRESENT: (
        "B_concept_tracking_only",
        "D_combined",
    ),
    CONCEPT_PRESENT_TO_ABSENT: (
        "A_neutral_control",
        "C_pure_task_induction",
    ),
}


@dataclass(frozen=True, slots=True)
class CrossMentionOuterFold:
    """One outer LODO fold in one concept-mention transfer direction."""

    test_domain: str
    direction: str
    training_group_ids: tuple[str, ...]
    test_group_ids: tuple[str, ...]
    training_item_ids: tuple[str, ...]
    test_item_ids: tuple[str, ...]
    training_cells: tuple[str, ...]
    test_cells: tuple[str, ...]

    def validate(self) -> None:
        if self.test_domain not in DOMAINS:
            raise ValidationError(f"unknown outer test domain {self.test_domain!r}")
        if self.direction not in TRANSFER_DIRECTIONS:
            raise ValidationError(f"unknown transfer direction {self.direction!r}")
        if set(self.training_group_ids) & set(self.test_group_ids):
            raise ValidationError("a matched group crosses the outer train/test boundary")
        if set(self.training_item_ids) & set(self.test_item_ids):
            raise ValidationError("an item crosses the outer train/test boundary")
        if self.training_cells != _SOURCE_CELLS[self.direction]:
            raise ValidationError("outer training cells do not match transfer source")
        if self.test_cells != _TARGET_CELLS[self.direction]:
            raise ValidationError("outer test cells do not match transfer target")


@dataclass(frozen=True, slots=True)
class InnerSelectionFold:
    """Training-only fold used to select layer and probe regularization."""

    outer_test_domain: str
    direction: str
    inner_fold_index: int
    training_group_ids: tuple[str, ...]
    validation_group_ids: tuple[str, ...]
    training_item_ids: tuple[str, ...]
    validation_item_ids: tuple[str, ...]

    def validate(self) -> None:
        if set(self.training_group_ids) & set(self.validation_group_ids):
            raise ValidationError("a matched group crosses an inner selection boundary")
        if set(self.training_item_ids) & set(self.validation_item_ids):
            raise ValidationError("an item crosses an inner selection boundary")


def _validated_groups(items: list[PromptItem]) -> dict[str, list[PromptItem]]:
    groups: dict[str, list[PromptItem]] = {}
    item_ids: set[str] = set()
    for item in items:
        if item.item_id in item_ids:
            raise ValidationError(f"duplicate item_id {item.item_id!r}")
        item_ids.add(item.item_id)
        groups.setdefault(item.matched_group_id, []).append(item)
    if not groups:
        raise ValidationError("cannot plan splits for an empty stimulus set")
    for gid, siblings in groups.items():
        if not is_complete_matched_group(siblings):
            raise ValidationError(f"matched group {gid!r} is not a complete A/B/C/D set")
    return groups


def plan_double_crossed_lodo(
    items: list[PromptItem], *, domains: tuple[str, ...] = DOMAINS
) -> tuple[CrossMentionOuterFold, ...]:
    """Plan all outer LODO folds in both concept-transfer directions.

    Whole matched groups are assigned by domain. The source-cell restriction says
    which siblings are used for fitting, while the target-cell restriction says
    which siblings are evaluated; unused siblings never migrate across the domain
    boundary.
    """

    groups = _validated_groups(items)
    observed_domains = {siblings[0].domain for siblings in groups.values()}
    if observed_domains != set(domains):
        raise ValidationError(
            "double-crossed LODO requires exactly the preregistered domains; "
            f"observed={sorted(observed_domains)} expected={sorted(domains)}"
        )

    folds: list[CrossMentionOuterFold] = []
    for test_domain in domains:
        train_gids = tuple(
            sorted(gid for gid, xs in groups.items() if xs[0].domain != test_domain)
        )
        test_gids = tuple(
            sorted(gid for gid, xs in groups.items() if xs[0].domain == test_domain)
        )
        if not train_gids or not test_gids:
            raise ValidationError(f"empty train or test side for domain {test_domain!r}")
        for direction in TRANSFER_DIRECTIONS:
            train_cells = _SOURCE_CELLS[direction]
            test_cells = _TARGET_CELLS[direction]
            train_ids = tuple(
                sorted(
                    item.item_id
                    for gid in train_gids
                    for item in groups[gid]
                    if item.cell in train_cells
                )
            )
            test_ids = tuple(
                sorted(
                    item.item_id
                    for gid in test_gids
                    for item in groups[gid]
                    if item.cell in test_cells
                )
            )
            fold = CrossMentionOuterFold(
                test_domain=test_domain,
                direction=direction,
                training_group_ids=train_gids,
                test_group_ids=test_gids,
                training_item_ids=train_ids,
                test_item_ids=test_ids,
                training_cells=train_cells,
                test_cells=test_cells,
            )
            fold.validate()
            folds.append(fold)
    return tuple(folds)


def plan_inner_selection_folds(
    items: list[PromptItem],
    outer_fold: CrossMentionOuterFold,
    *,
    n_splits: int = 3,
) -> tuple[InnerSelectionFold, ...]:
    """Create nested matched-group folds using outer-training groups only.

    Layer and regularization selection must consume only the returned training and
    validation item identifiers. No identifier from the outer held-out domain can
    appear in these folds.
    """

    outer_fold.validate()
    if n_splits < 2:
        raise ValidationError("inner selection requires at least two folds")
    groups = _validated_groups(items)
    eligible = tuple(sorted(outer_fold.training_group_ids))
    if len(eligible) < n_splits:
        raise ValidationError("fewer outer-training groups than inner folds")
    if any(groups[gid][0].domain == outer_fold.test_domain for gid in eligible):
        raise ValidationError("outer test-domain group leaked into selection input")

    result: list[InnerSelectionFold] = []
    for fold_index in range(n_splits):
        validation_gids = tuple(eligible[fold_index::n_splits])
        training_gids = tuple(gid for gid in eligible if gid not in validation_gids)
        training_ids = tuple(
            sorted(
                item.item_id
                for gid in training_gids
                for item in groups[gid]
                if item.cell in _SOURCE_CELLS[outer_fold.direction]
            )
        )
        validation_ids = tuple(
            sorted(
                item.item_id
                for gid in validation_gids
                for item in groups[gid]
                if item.cell in _TARGET_CELLS[outer_fold.direction]
            )
        )
        fold = InnerSelectionFold(
            outer_test_domain=outer_fold.test_domain,
            direction=outer_fold.direction,
            inner_fold_index=fold_index,
            training_group_ids=training_gids,
            validation_group_ids=validation_gids,
            training_item_ids=training_ids,
            validation_item_ids=validation_ids,
        )
        fold.validate()
        result.append(fold)
    return tuple(result)
