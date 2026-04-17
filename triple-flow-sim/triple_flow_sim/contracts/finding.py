"""Pydantic models for findings and the classification taxonomy.

Spec reference: files/finding-schema.md
"""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Optional
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field


# -----------------------------------------------------------------------------
# Taxonomy enums
# -----------------------------------------------------------------------------

class Layer(str, Enum):
    CIM = "CIM"
    PIM = "PIM"
    PSM = "PSM"
    NA = "N/A"


class Generator(str, Enum):
    INVENTORY = "inventory"
    STATIC_HANDOFF = "static_handoff"
    GROUNDED_PAIR = "grounded_pair"
    SEQUENCE_RUN = "sequence_run"
    CONTEXT_ISOLATION = "context_isolation"
    BRANCH_BOUNDARY = "branch_boundary"
    PERTURBATION = "perturbation"
    ABLATION = "ablation"
    VOLUME = "volume"


class Severity(str, Enum):
    REGULATORY = "regulatory"
    CORRECTNESS = "correctness"
    EFFICIENCY = "efficiency"
    COSMETIC = "cosmetic"


class Confidence(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class FindingStatus(str, Enum):
    NEW = "new"
    TRIAGED = "triaged"
    ACCEPTED = "accepted"
    SUPPRESSED = "suppressed"
    FIXED = "fixed"
    REGRESSED = "regressed"


class DefectClass(str, Enum):
    # Structure defects
    LAYER_MISSING = "layer_missing"
    IDENTITY_INCOMPLETE = "identity_incomplete"
    ORPHAN_TRIPLE = "orphan_triple"
    ORPHAN_OBLIGATION = "orphan_obligation"
    REGULATORY_ORPHAN = "regulatory_orphan"

    # Contract defects
    CONTRACT_MISSING = "contract_missing"
    OUTPUT_UNDER_DECLARATION = "output_under_declaration"
    OUTPUT_OVER_PROMISE = "output_over_promise"
    INPUT_UNDER_DECLARATION = "input_under_declaration"
    TYPE_MISMATCH = "type_mismatch"
    STATE_FLOW_GAP = "state_flow_gap"
    SILENT_OVERWRITE = "silent_overwrite"

    # Decision defects
    EVALUABILITY_GAP = "evaluability_gap"
    PREDICATE_NON_PARTITIONING = "predicate_non_partitioning"
    BRANCH_MISDIRECTION = "branch_misdirection"
    ESCALATION_FAILURE = "escalation_failure"

    # Content defects
    CONTENT_MISSING = "content_missing"
    CONTENT_STALE = "content_stale"
    CONTENT_ADJACENT_NOT_ACTIONABLE = "content_adjacent_not_actionable"
    CONTENT_CONTRADICTS = "content_contradicts"

    # Handoff defects (core value)
    HANDOFF_CARRIED_BY_EXTERNAL_CONTEXT = "handoff_carried_by_external_context"
    HANDOFF_FORMAT_MISMATCH = "handoff_format_mismatch"
    HANDOFF_IMPLICIT_SETUP = "handoff_implicit_setup"
    HANDOFF_NAMING_DRIFT = "handoff_naming_drift"

    # Journey-level defects
    CUMULATIVE_DRIFT = "cumulative_drift"
    CONTEXT_BLOAT = "context_bloat"
    JOURNEY_STUCK = "journey_stuck"
    REGULATORY_VIOLATION = "regulatory_violation"


# -----------------------------------------------------------------------------
# Finding record and supporting models
# -----------------------------------------------------------------------------

class Evidence(BaseModel):
    """Evidence block embedded in a finding. Spec: files/finding-schema.md."""
    model_config = ConfigDict(extra="allow")

    journey_id: Optional[str] = None
    step_index: Optional[int] = None
    observed: Any = None
    expected: Any = None
    trace_ref: str = ""


class RawDetection(BaseModel):
    """Unclassified signal emitted by a detector.

    The classifier (component 11) converts RawDetection → Finding by assigning
    defect_class, layer, severity, and rendering summary/detail.
    Spec reference: files/11-finding-classifier.md.
    """
    model_config = ConfigDict(extra="allow")

    signal_type: str                         # Detector-specific key into rules.yaml
    generator: Generator                     # Which component emitted it
    primary_triple_id: Optional[str] = None
    related_triple_ids: list[str] = Field(default_factory=list)
    bpmn_node_id: Optional[str] = None
    bpmn_edge_id: Optional[str] = None
    detector_context: dict = Field(default_factory=dict)  # Signal-specific data
    evidence: Optional[Evidence] = None


class Finding(BaseModel):
    """A classified defect record. Spec: files/finding-schema.md §Finding record."""
    model_config = ConfigDict(extra="allow")

    finding_id: str = Field(default_factory=lambda: str(uuid4()))
    detected_at: datetime = Field(default_factory=datetime.utcnow)
    taxonomy_version: str = "1.0.0"

    # Classification
    layer: Layer
    defect_class: DefectClass
    generator: Generator
    severity: Severity = Severity.CORRECTNESS
    confidence: Confidence = Confidence.HIGH

    # Attribution
    primary_triple_id: str = ""
    related_triple_ids: list[str] = Field(default_factory=list)
    bpmn_node_id: str = ""
    bpmn_edge_id: Optional[str] = None

    # Evidence
    summary: str = ""
    detail: str = ""
    evidence: Evidence = Field(default_factory=Evidence)

    # Blast radius (populated by finding store on insertion)
    journeys_affected_count: int = 0
    journeys_affected_pct: float = 0.0
    is_on_critical_path: bool = False

    # Lifecycle
    status: FindingStatus = FindingStatus.NEW
    suppression_reason: Optional[str] = None
    first_seen_run: str = ""
    last_seen_run: str = ""
    occurrence_count: int = 1
