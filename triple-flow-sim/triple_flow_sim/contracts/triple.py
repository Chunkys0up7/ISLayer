"""Pydantic models for the triple schema.

Spec reference: files/triple-schema.md
"""
from __future__ import annotations

from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


# -----------------------------------------------------------------------------
# Enums
# -----------------------------------------------------------------------------

class BpmnNodeType(str, Enum):
    TASK = "task"
    EXCLUSIVE_GATEWAY = "exclusive_gateway"
    PARALLEL_GATEWAY = "parallel_gateway"
    START_EVENT = "start_event"
    END_EVENT = "end_event"
    INTERMEDIATE_EVENT = "intermediate_event"


class ContentType(str, Enum):
    KNOWLEDGE = "knowledge"
    REGULATORY = "regulatory"
    JOB_AID = "job_aid"


class ObligationType(str, Enum):
    OPENS = "opens"
    CLOSES = "closes"
    ENFORCES = "enforces"
    REFERENCES = "references"


class AssertionPredicate(str, Enum):
    EXISTS = "exists"
    EQUALS = "equals"
    IN_RANGE = "in_range"
    MATCHES_PATTERN = "matches_pattern"
    SATISFIES_EXPRESSION = "satisfies_expression"


# -----------------------------------------------------------------------------
# Subtypes (files/triple-schema.md §Subtype definitions)
# -----------------------------------------------------------------------------

class StateFieldRef(BaseModel):
    model_config = ConfigDict(extra="allow")

    path: str
    type: str = "any"
    namespace: Optional[str] = None


class ContextAssertion(BaseModel):
    model_config = ConfigDict(extra="allow")

    path: str
    predicate: AssertionPredicate = AssertionPredicate.EXISTS
    value: Any = None
    type: str = "any"
    source_triple: Optional[str] = None


class MustCloseBy(BaseModel):
    model_config = ConfigDict(extra="allow")

    condition: str
    anchor: Optional[StateFieldRef] = None


class ObligationSpec(BaseModel):
    model_config = ConfigDict(extra="allow")

    obligation_id: str
    description: str = ""
    regulatory_ref: Optional[str] = None
    must_close_by: Optional[MustCloseBy] = None
    close_conditions: list[ContextAssertion] = Field(default_factory=list)
    exits_journey: bool = False


class BranchPredicate(BaseModel):
    model_config = ConfigDict(extra="allow")

    edge_id: str
    predicate_expression: str
    evidence_refs: list[str] = Field(default_factory=list)
    is_default: bool = False


class RetrievalMetadata(BaseModel):
    model_config = ConfigDict(extra="allow")

    retrieved_at: Optional[str] = None
    retrieval_confidence: Optional[float] = None
    source_span: Optional[dict] = None


class ContentChunk(BaseModel):
    model_config = ConfigDict(extra="allow")

    chunk_id: str
    source_document: str = ""
    content_type: ContentType = ContentType.KNOWLEDGE
    text: str = ""
    retrieval_metadata: Optional[RetrievalMetadata] = None


class ToolRef(BaseModel):
    model_config = ConfigDict(extra="allow")

    tool_id: str
    purpose: str = ""
    mock_response_template: Optional[str] = None


class RegulatoryRef(BaseModel):
    model_config = ConfigDict(extra="allow")

    citation: str
    rule_text: str = ""
    obligation_type: ObligationType = ObligationType.REFERENCES


class BusinessRule(BaseModel):
    model_config = ConfigDict(extra="allow")

    rule_id: str
    rule_text: str = ""
    evaluable_form: Optional[str] = None


# -----------------------------------------------------------------------------
# Layer objects
# -----------------------------------------------------------------------------

class CIMLayer(BaseModel):
    model_config = ConfigDict(extra="allow")

    intent: str = ""
    regulatory_refs: list[RegulatoryRef] = Field(default_factory=list)
    business_rules: list[BusinessRule] = Field(default_factory=list)


class PIMLayer(BaseModel):
    """PIM layer.

    Note: fields may be absent (None) to distinguish "not declared" from
    "explicitly empty". This matters for invariant I4 (contract_missing)
    and for I7 (state_flow_gap). See files/triple-schema.md §Required invariants.
    """
    model_config = ConfigDict(extra="allow")

    preconditions: Optional[list[ContextAssertion]] = None
    postconditions: Optional[list[ContextAssertion]] = None
    obligations_opened: Optional[list[ObligationSpec]] = None
    obligations_closed: Optional[list[str]] = None  # list of obligation_id
    decision_predicates: Optional[list[BranchPredicate]] = None  # required for gateways
    state_writes: Optional[list[StateFieldRef]] = None
    state_reads: Optional[list[StateFieldRef]] = None


class PSMLayer(BaseModel):
    model_config = ConfigDict(extra="allow")

    enriched_content: list[ContentChunk] = Field(default_factory=list)
    prompt_scaffold: Optional[str] = None
    tool_bindings: list[ToolRef] = Field(default_factory=list)


# -----------------------------------------------------------------------------
# Triple and TripleSet
# -----------------------------------------------------------------------------

class Triple(BaseModel):
    """A single triple conforming to files/triple-schema.md."""
    model_config = ConfigDict(extra="allow")

    # Identity (required per I1)
    triple_id: str
    version: str = "0"
    bpmn_node_id: str = ""
    bpmn_node_type: BpmnNodeType = BpmnNodeType.TASK

    # Layers — note: required by I2 but may be None at load time (becomes a finding)
    cim: Optional[CIMLayer] = None
    pim: Optional[PIMLayer] = None
    psm: Optional[PSMLayer] = None

    # Provenance
    source_path: Optional[str] = None  # From loader B8 / _source_path
    raw: Optional[dict] = None          # Preserved original if strict_mode=false and unmappable


class TripleSet(BaseModel):
    """Collection of triples keyed by triple_id."""
    model_config = ConfigDict(extra="allow")

    triples: dict[str, Triple] = Field(default_factory=dict)
    corpus_version_hash: str = ""

    def __iter__(self):
        return iter(self.triples.values())

    def __len__(self) -> int:
        return len(self.triples)

    def __contains__(self, triple_id: str) -> bool:
        return triple_id in self.triples

    def get(self, triple_id: str) -> Optional[Triple]:
        return self.triples.get(triple_id)


class LoadReport(BaseModel):
    """Output of component 01 alongside TripleSet.

    Spec reference: files/01-triple-loader.md §Outputs.
    """
    model_config = ConfigDict(extra="allow")

    total_files_attempted: int = 0
    successful_loads: int = 0
    failed_loads: list[dict] = Field(default_factory=list)  # [{path, error}]
    identity_failures: list[dict] = Field(default_factory=list)  # [{path, missing_fields}]
    field_mapping_applied: dict = Field(default_factory=dict)
    raw_preservation: list[str] = Field(default_factory=list)  # triple_ids with _raw preserved
    corpus_version_hash: str = ""
    source_format: str = ""
    source_path: str = ""
