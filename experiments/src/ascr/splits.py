"""Design-time split and resampling planners for the ASCR v0.1.2 analyses.

The functions in this module operate only on prompt metadata. They do not load a
model, activations, outputs, or scientific observations. Their purpose is to make
the double-crossed leave-one-domain-out boundary, the inner
leave-one-training-domain-out selection boundary, and the domain-stratified
matched-group cluster bootstrap mechanically inspectable before data collection.

Nothing here produces a prediction, a loss, a statistic, or any scientific
observation. The bootstrap planner returns only which ``matched_group_id``
clusters a replicate would draw; it never touches model output.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from math import ceil
from typing import Final

from .schema import (
    RESPONSE_LABEL_RELIABILITY_FRACTION,
    RESPONSE_LABEL_RELIABILITY_SEED,
    PromptItem,
    ValidationError,
    is_complete_matched_group,
)
from .strategy_labels import DOMAINS

CONCEPT_ABSENT_TO_PRESENT: Final[str] = "concept_absent_to_present"
CONCEPT_PRESENT_TO_ABSENT: Final[str] = "concept_present_to_absent"
TRANSFER_DIRECTIONS: Final[tuple[str, ...]] = (
    CONCEPT_ABSENT_TO_PRESENT,
    CONCEPT_PRESENT_TO_ABSENT,
)

#: Number of inner selection folds implied by leave-one-training-domain-out with
#: the four registered domains: one outer test domain leaves exactly three
#: training domains, and each is held out once as the inner validation domain.
INNER_LODO_FOLDS: Final[int] = len(DOMAINS) - 1

#: Registered number of cluster-bootstrap resamples (frozen pre-data).
BOOTSTRAP_RESAMPLES: Final[int] = 1000

#: Registered bootstrap seed (frozen pre-data; see ``analysis.bootstrap_seed``).
BOOTSTRAP_SEED: Final[int] = 20260830

#: Registered permutation seed (frozen pre-data; see ``analysis.permutation_seed``).
PERMUTATION_SEED: Final[int] = 20260831

#: Registered number of random permutations for every secondary raw p-value.
PERMUTATION_REPLICATES: Final[int] = 10000

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
            raise ValidationError(
                "a matched group crosses the outer train/test boundary"
            )
        if set(self.training_item_ids) & set(self.test_item_ids):
            raise ValidationError("an item crosses the outer train/test boundary")
        if self.training_cells != _SOURCE_CELLS[self.direction]:
            raise ValidationError("outer training cells do not match transfer source")
        if self.test_cells != _TARGET_CELLS[self.direction]:
            raise ValidationError("outer test cells do not match transfer target")


@dataclass(frozen=True, slots=True)
class InnerSelectionFold:
    """One inner leave-one-training-domain-out selection fold.

    Exactly one of the three outer-training domains is held out as the inner
    validation domain; the other two form the inner fit set. The concept-transfer
    direction stays crossed: source-concept cells of the two inner-fit domains fit
    the candidate, and opposite-concept cells of the inner-validation domain score
    it. No outer-test-domain group or item may appear on either side.
    """

    outer_test_domain: str
    direction: str
    inner_fold_index: int
    inner_validation_domain: str
    inner_training_domains: tuple[str, ...]
    training_group_ids: tuple[str, ...]
    validation_group_ids: tuple[str, ...]
    training_item_ids: tuple[str, ...]
    validation_item_ids: tuple[str, ...]

    def validate(self) -> None:
        if self.outer_test_domain not in DOMAINS:
            raise ValidationError(
                f"unknown outer test domain {self.outer_test_domain!r}"
            )
        if self.direction not in TRANSFER_DIRECTIONS:
            raise ValidationError(f"unknown transfer direction {self.direction!r}")
        if self.inner_validation_domain not in DOMAINS:
            raise ValidationError(
                f"unknown inner validation domain {self.inner_validation_domain!r}"
            )
        if self.inner_validation_domain == self.outer_test_domain:
            raise ValidationError("outer test domain leaked into inner selection")
        if self.outer_test_domain in self.inner_training_domains:
            raise ValidationError("outer test domain leaked into inner selection")
        if self.inner_validation_domain in self.inner_training_domains:
            raise ValidationError(
                "the inner validation domain cannot also be an inner fit domain"
            )
        if len(self.inner_training_domains) != INNER_LODO_FOLDS - 1:
            raise ValidationError(
                "inner leave-one-training-domain-out requires exactly "
                f"{INNER_LODO_FOLDS - 1} inner fit domains, got "
                f"{len(self.inner_training_domains)}"
            )
        if set(self.training_group_ids) & set(self.validation_group_ids):
            raise ValidationError("a matched group crosses an inner selection boundary")
        if set(self.training_item_ids) & set(self.validation_item_ids):
            raise ValidationError("an item crosses an inner selection boundary")


@dataclass(frozen=True, slots=True)
class ClusterBootstrapPlan:
    """One domain-stratified matched-group cluster-bootstrap replicate plan.

    ``drawn_group_ids`` lists the ``matched_group_id`` clusters this replicate
    draws, with replacement, from the held-out matched groups. Each held-out
    domain contributes exactly as many groups as it contributed to the observed
    aggregate, so the domain strata are preserved. Every prediction belonging to a
    drawn group travels with it; items, cells, directions, and seeds are never
    resampled as if independent.
    """

    replicate_index: int
    seed: int
    drawn_group_ids: tuple[str, ...]
    groups_per_domain: tuple[tuple[str, int], ...]

    def validate(self) -> None:
        if self.replicate_index < 0:
            raise ValidationError("bootstrap replicate index must be non-negative")
        expected = sum(count for _, count in self.groups_per_domain)
        if len(self.drawn_group_ids) != expected:
            raise ValidationError(
                "a cluster-bootstrap replicate must draw exactly as many groups as "
                f"the observed aggregate ({expected}), got {len(self.drawn_group_ids)}"
            )


@dataclass(frozen=True, slots=True)
class ReliabilitySubsetPlan:
    """Pre-label deterministic second-reviewer matched-group subset."""

    seed: int
    fraction: float
    total_complete_groups: int
    selected_group_ids: tuple[str, ...]
    selected_groups_per_domain: tuple[tuple[str, int], ...]

    def validate(self) -> None:
        expected = ceil(self.fraction * self.total_complete_groups)
        if len(self.selected_group_ids) != expected:
            raise ValidationError(
                f"reliability subset must contain ceil({self.fraction} * "
                f"{self.total_complete_groups}) = {expected} groups"
            )
        counts = [count for _, count in self.selected_groups_per_domain]
        if counts and max(counts) - min(counts) > 1:
            raise ValidationError(
                "reliability subset must be domain-stratified as evenly as possible"
            )


def _validated_groups(
    items: list[PromptItem], *, target_axis: str | None = None
) -> dict[str, list[PromptItem]]:
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
            raise ValidationError(
                f"matched group {gid!r} is not a complete A/B/C/D set"
            )
    observed_axes = {siblings[0].axis for siblings in groups.values()}
    if len(observed_axes) != 1:
        raise ValidationError(
            "a scientific split plan must contain exactly one target axis; "
            f"observed={sorted(observed_axes)}"
        )
    if target_axis is not None and observed_axes != {target_axis}:
        raise ValidationError(
            f"split target axis mismatch: observed={sorted(observed_axes)} "
            f"expected={[target_axis]}"
        )
    return groups


def plan_double_crossed_lodo(
    items: list[PromptItem],
    *,
    domains: tuple[str, ...] = DOMAINS,
    target_axis: str | None = None,
) -> tuple[CrossMentionOuterFold, ...]:
    """Plan all outer LODO folds in both concept-transfer directions.

    Whole matched groups are assigned by domain. The source-cell restriction says
    which siblings are used for fitting, while the target-cell restriction says
    which siblings are evaluated; unused siblings never migrate across the domain
    boundary.
    """

    groups = _validated_groups(items, target_axis=target_axis)
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
            raise ValidationError(
                f"empty train or test side for domain {test_domain!r}"
            )
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
    domains: tuple[str, ...] = DOMAINS,
) -> tuple[InnerSelectionFold, ...]:
    """Plan deterministic inner leave-one-training-domain-out selection folds.

    For an outer fold, exactly three training domains remain. Each inner fold
    holds out one of them for validation while the other two form the inner fit
    set, so the inner boundary mirrors the outer cross-domain claim instead of
    mixing domains. Whole matched groups stay disjoint, the concept-transfer
    direction stays crossed, and no identifier from the outer held-out domain can
    appear in these folds.

    Layer and regularization selection must consume only the returned training and
    validation item identifiers.
    """

    outer_fold.validate()
    groups = _validated_groups(items)
    eligible = tuple(sorted(outer_fold.training_group_ids))
    if any(groups[gid][0].domain == outer_fold.test_domain for gid in eligible):
        raise ValidationError("outer test-domain group leaked into selection input")

    training_domains = tuple(d for d in domains if d != outer_fold.test_domain)
    if len(training_domains) != INNER_LODO_FOLDS:
        raise ValidationError(
            "inner leave-one-training-domain-out requires exactly "
            f"{INNER_LODO_FOLDS} outer-training domains, got {len(training_domains)}"
        )
    observed = {groups[gid][0].domain for gid in eligible}
    missing = [d for d in training_domains if d not in observed]
    if missing:
        raise ValidationError(
            f"outer-training domains without any matched group: {sorted(missing)}"
        )

    result: list[InnerSelectionFold] = []
    for fold_index, validation_domain in enumerate(training_domains):
        fit_domains = tuple(d for d in training_domains if d != validation_domain)
        validation_gids = tuple(
            gid for gid in eligible if groups[gid][0].domain == validation_domain
        )
        training_gids = tuple(
            gid for gid in eligible if groups[gid][0].domain in fit_domains
        )
        if not validation_gids or not training_gids:
            raise ValidationError(
                "empty inner fit or inner validation side for validation domain "
                f"{validation_domain!r}"
            )
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
            inner_validation_domain=validation_domain,
            inner_training_domains=fit_domains,
            training_group_ids=training_gids,
            validation_group_ids=validation_gids,
            training_item_ids=training_ids,
            validation_item_ids=validation_ids,
        )
        fold.validate()
        result.append(fold)
    return tuple(result)


def held_out_groups_by_domain(
    items: list[PromptItem],
    *,
    domains: tuple[str, ...] = DOMAINS,
    target_axis: str | None = None,
) -> tuple[tuple[str, tuple[str, ...]], ...]:
    """Return the complete matched groups of each domain, in registered order.

    Under pooled bidirectional LODO every matched group is held out exactly once
    (in the fold whose outer test domain is its own), and it then contributes its
    four out-of-fold cell predictions: cells B/D in the absent-to-present
    direction and cells A/C in the present-to-absent direction.
    """

    groups = _validated_groups(items, target_axis=target_axis)
    by_domain: dict[str, list[str]] = {domain: [] for domain in domains}
    for gid, siblings in groups.items():
        domain = siblings[0].domain
        if domain not in by_domain:
            raise ValidationError(f"unregistered domain {domain!r} in stimulus set")
        by_domain[domain].append(gid)
    missing = [domain for domain in domains if not by_domain[domain]]
    if missing:
        raise ValidationError(
            f"held-out strata require every registered domain; missing={missing}"
        )
    return tuple((domain, tuple(sorted(by_domain[domain]))) for domain in domains)


def plan_cluster_bootstrap(
    items: list[PromptItem],
    *,
    resamples: int = BOOTSTRAP_RESAMPLES,
    seed: int = BOOTSTRAP_SEED,
    domains: tuple[str, ...] = DOMAINS,
    target_axis: str | None = None,
) -> tuple[ClusterBootstrapPlan, ...]:
    """Plan the registered domain-stratified matched-group cluster bootstrap.

    Complete ``matched_group_id`` clusters are resampled with replacement inside
    each held-out domain, so every domain contributes exactly the number of groups
    it contributed to the observed aggregate. All predictions attached to a drawn
    group travel with it. This planner returns group identifiers only; it computes
    no statistic and touches no model output.
    """

    if resamples < 1:
        raise ValidationError("cluster bootstrap requires at least one resample")
    strata = held_out_groups_by_domain(items, domains=domains, target_axis=target_axis)
    if not strata:
        raise ValidationError("cluster bootstrap requires at least one held-out domain")
    counts = tuple((domain, len(gids)) for domain, gids in strata)

    plans: list[ClusterBootstrapPlan] = []
    for replicate_index in range(resamples):
        # A per-replicate stream derived from the frozen seed keeps the whole plan
        # reproducible and independent of iteration order elsewhere. The derivation
        # string is part of the registered procedure.
        rng = random.Random(f"ascr-cluster-bootstrap:{seed}:{replicate_index}")
        drawn: list[str] = []
        for domain, gids in strata:
            drawn.extend(rng.choices(gids, k=len(gids)))
        plan = ClusterBootstrapPlan(
            replicate_index=replicate_index,
            seed=seed,
            drawn_group_ids=tuple(drawn),
            groups_per_domain=counts,
        )
        plan.validate()
        plans.append(plan)
    return tuple(plans)


def plan_response_label_reliability_subset(
    items: list[PromptItem],
    *,
    fraction: float = RESPONSE_LABEL_RELIABILITY_FRACTION,
    seed: int = RESPONSE_LABEL_RELIABILITY_SEED,
    domains: tuple[str, ...] = DOMAINS,
    target_axis: str | None = None,
) -> ReliabilitySubsetPlan:
    """Select the independent second-labeler subset before labels are observed.

    Complete matched groups are selected deterministically, with group identifiers
    shuffled independently inside each registered domain and allocations made in a
    registered-domain round robin. This uses prompt metadata only.
    """

    if not (0.0 < fraction <= 1.0):
        raise ValidationError("reliability subset fraction must be in (0, 1]")
    strata = held_out_groups_by_domain(items, domains=domains, target_axis=target_axis)
    pools: dict[str, list[str]] = {}
    for domain, group_ids in strata:
        pool = list(group_ids)
        random.Random(f"ascr-response-label-reliability:{seed}:{domain}").shuffle(pool)
        pools[domain] = pool
    total = sum(len(group_ids) for _, group_ids in strata)
    required = ceil(fraction * total)
    selected: dict[str, list[str]] = {domain: [] for domain in domains}
    while sum(len(ids) for ids in selected.values()) < required:
        progressed = False
        for domain in domains:
            if pools[domain] and sum(len(ids) for ids in selected.values()) < required:
                selected[domain].append(pools[domain].pop())
                progressed = True
        if not progressed:  # pragma: no cover - guarded by required <= total
            raise ValidationError("not enough groups for reliability subset")
    plan = ReliabilitySubsetPlan(
        seed=seed,
        fraction=fraction,
        total_complete_groups=total,
        selected_group_ids=tuple(
            gid for domain in domains for gid in sorted(selected[domain])
        ),
        selected_groups_per_domain=tuple(
            (domain, len(selected[domain])) for domain in domains
        ),
    )
    plan.validate()
    return plan
