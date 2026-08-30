"""Pure design-time helpers for ASCR token indexing and Layer-0 pooling."""

from __future__ import annotations

from collections.abc import Sequence

from .schema import ValidationError


def final_non_padding_index(attention_mask: Sequence[int | bool]) -> int:
    """Return the last index whose attention-mask value is one.

    This definition is independent of left/right padding and is the registered
    indexing rule for the final prompt token.
    """

    if not attention_mask:
        raise ValidationError("attention_mask must be non-empty")
    invalid = [x for x in attention_mask if x not in (0, 1, False, True)]
    if invalid:
        raise ValidationError("attention_mask must contain only binary values")
    positions = [i for i, value in enumerate(attention_mask) if bool(value)]
    if not positions:
        raise ValidationError("attention_mask contains no non-padding token")
    return positions[-1]


def user_content_pool_mask(
    user_content_mask: Sequence[int | bool],
    attention_mask: Sequence[int | bool],
    special_tokens_mask: Sequence[int | bool],
) -> tuple[bool, ...]:
    """Return the exact Layer-0 pooling mask.

    A token is included only when it is in the human-visible user-content span,
    is not padding, and is not a tokenizer special/template token.
    """

    lengths = {len(user_content_mask), len(attention_mask), len(special_tokens_mask)}
    if len(lengths) != 1 or not lengths or next(iter(lengths)) == 0:
        raise ValidationError("all non-empty token masks must have equal length")
    for name, mask in (
        ("user_content_mask", user_content_mask),
        ("attention_mask", attention_mask),
        ("special_tokens_mask", special_tokens_mask),
    ):
        if any(x not in (0, 1, False, True) for x in mask):
            raise ValidationError(f"{name} must contain only binary values")
    result = tuple(
        bool(user) and bool(attend) and not bool(special)
        for user, attend, special in zip(
            user_content_mask, attention_mask, special_tokens_mask
        )
    )
    if not any(result):
        raise ValidationError("Layer-0 pooling mask selects no user-content token")
    return result


def mean_pool_user_content_embeddings(
    token_embeddings: Sequence[Sequence[float]],
    user_content_mask: Sequence[int | bool],
    attention_mask: Sequence[int | bool],
    special_tokens_mask: Sequence[int | bool],
) -> tuple[float, ...]:
    """Mean-pool Layer-0 embeddings over the registered user-content mask."""

    if len(token_embeddings) != len(user_content_mask):
        raise ValidationError("token embeddings and masks must have equal length")
    mask = user_content_pool_mask(
        user_content_mask, attention_mask, special_tokens_mask
    )
    selected = [row for row, include in zip(token_embeddings, mask) if include]
    dimensions = {len(row) for row in token_embeddings}
    if len(dimensions) != 1 or not dimensions or next(iter(dimensions)) == 0:
        raise ValidationError("token embeddings must have one non-zero dimension")
    dimension = next(iter(dimensions))
    return tuple(
        sum(float(row[j]) for row in selected) / len(selected)
        for j in range(dimension)
    )
