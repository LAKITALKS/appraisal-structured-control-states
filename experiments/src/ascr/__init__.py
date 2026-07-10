"""ASCR pilot scaffold.

Design-time utilities for the preregistered Appraisal-Structured Latent Control
Representations pilot: typed prompt-item schemas, the 2x2 design-cell labels, the
response-strategy taxonomy, and config validation.

This package does not run any model. It exists so that the pilot dataset and
configuration are machine-checkable before any activations are extracted.
"""

from __future__ import annotations

from .schema import (
    PilotConfig,
    PromptItem,
    ValidationError,
    item_from_dict,
    load_config,
    parse_config,
    validate_matched_group,
)
from .strategy_labels import (
    AXES,
    DESIGN_CELLS,
    DOMAINS,
    EXPLORATORY_AXES,
    PRIMARY_AXES,
    RESPONSE_STRATEGIES,
    design_cell,
    is_primary_axis,
    is_valid_strategy,
)

__version__ = "0.1.0"

__all__ = [
    "AXES",
    "DESIGN_CELLS",
    "DOMAINS",
    "EXPLORATORY_AXES",
    "PRIMARY_AXES",
    "PilotConfig",
    "PromptItem",
    "RESPONSE_STRATEGIES",
    "ValidationError",
    "design_cell",
    "is_primary_axis",
    "is_valid_strategy",
    "item_from_dict",
    "load_config",
    "parse_config",
    "validate_matched_group",
    "__version__",
]
