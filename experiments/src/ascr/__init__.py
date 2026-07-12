"""ASCR pilot scaffold.

Design-time utilities for the preregistered Appraisal-Structured Latent Control
Representations pilot: typed prompt-item schemas, the 2x2 design-cell labels, the
response-strategy taxonomy, and config validation.

This package does not run any model. It exists so that the pilot dataset and
configuration are machine-checkable before any activations are extracted.
"""

from __future__ import annotations

from .schema import (
    PLACEHOLDER_MODEL_REVISION,
    PLACEHOLDER_REPLICATION_MODEL,
    REQUIRED_QA_FIELDS,
    PilotConfig,
    PromptItem,
    RunManifest,
    ValidationError,
    is_complete_matched_group,
    is_placeholder_revision,
    item_from_dict,
    load_config,
    manifests_compatible,
    parse_config,
    validate_matched_group,
    validate_qa,
)
from .strategy_labels import (
    AXES,
    DESIGN_CELLS,
    DOMAINS,
    EXPLORATORY_AXES,
    FINE_TO_SUPERCLASS,
    PRIMARY_AXES,
    RESPONSE_STRATEGIES,
    STRATEGY_SUPERCLASSES,
    design_cell,
    is_primary_axis,
    is_valid_strategy,
    superclass_of,
)

__version__ = "0.1.1"

__all__ = [
    "AXES",
    "DESIGN_CELLS",
    "DOMAINS",
    "EXPLORATORY_AXES",
    "FINE_TO_SUPERCLASS",
    "PLACEHOLDER_MODEL_REVISION",
    "PLACEHOLDER_REPLICATION_MODEL",
    "PRIMARY_AXES",
    "REQUIRED_QA_FIELDS",
    "PilotConfig",
    "PromptItem",
    "RESPONSE_STRATEGIES",
    "RunManifest",
    "STRATEGY_SUPERCLASSES",
    "ValidationError",
    "design_cell",
    "is_complete_matched_group",
    "is_placeholder_revision",
    "is_primary_axis",
    "is_valid_strategy",
    "item_from_dict",
    "load_config",
    "manifests_compatible",
    "parse_config",
    "superclass_of",
    "validate_matched_group",
    "validate_qa",
    "__version__",
]
