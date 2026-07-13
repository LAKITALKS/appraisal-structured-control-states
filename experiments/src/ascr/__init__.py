"""ASCR pilot scaffold.

Design-time utilities for the preregistered Appraisal-Structured Latent Control
Representations pilot: typed prompt-item schemas, the 2x2 design-cell labels, the
response-strategy taxonomy, and config validation.

This package does not run any model. It exists so that the pilot dataset and
configuration are machine-checkable before any activations are extracted.
"""

from __future__ import annotations

from .schema import (
    EXTERNAL_PROVENANCE_FIELDS,
    PLACEHOLDER_MODEL_REVISION,
    PLACEHOLDER_REPLICATION_MODEL,
    PROVENANCE_DECISIONS,
    QA_BOOLEAN_FIELDS,
    QA_DISPOSITIONS,
    QA_MODES,
    REQUIRED_QA_FIELDS,
    PilotConfig,
    PromptItem,
    RunManifest,
    ValidationError,
    check_run_ready,
    is_complete_matched_group,
    is_placeholder_revision,
    is_run_ready,
    item_from_dict,
    load_config,
    manifests_compatible,
    parse_config,
    provenance_is_run_ready,
    qa_item_passes,
    validate_matched_group,
    validate_provenance,
    validate_qa,
    validate_run_ready_group,
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
    SUPERCLASS_DOMINANCE,
    design_cell,
    dominant_superclass,
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
    "EXTERNAL_PROVENANCE_FIELDS",
    "FINE_TO_SUPERCLASS",
    "PLACEHOLDER_MODEL_REVISION",
    "PLACEHOLDER_REPLICATION_MODEL",
    "PROVENANCE_DECISIONS",
    "PRIMARY_AXES",
    "QA_BOOLEAN_FIELDS",
    "QA_DISPOSITIONS",
    "QA_MODES",
    "REQUIRED_QA_FIELDS",
    "PilotConfig",
    "PromptItem",
    "RESPONSE_STRATEGIES",
    "RunManifest",
    "STRATEGY_SUPERCLASSES",
    "SUPERCLASS_DOMINANCE",
    "ValidationError",
    "check_run_ready",
    "design_cell",
    "dominant_superclass",
    "is_complete_matched_group",
    "is_placeholder_revision",
    "is_run_ready",
    "is_primary_axis",
    "is_valid_strategy",
    "item_from_dict",
    "load_config",
    "manifests_compatible",
    "parse_config",
    "provenance_is_run_ready",
    "qa_item_passes",
    "superclass_of",
    "validate_matched_group",
    "validate_provenance",
    "validate_qa",
    "validate_run_ready_group",
    "__version__",
]
