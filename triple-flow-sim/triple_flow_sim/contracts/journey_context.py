"""Pydantic models for JourneyContext.

Spec reference: files/journey-context.md

Note: Phase 1 builds these models for forward compatibility (Phase 3 populates
them). Mutation discipline M1-M5 is enforced by the sequence runner (component 06),
not in Phase 1.
"""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field

from triple_flow_sim.contracts.triple import ContextAssertion, StateFieldRef


class ExecutionMode(str, Enum):
    STATIC = "static"
    GROUNDED = "grounded"
    ISOLATED = "isolated"


class ProvenanceEntry(BaseModel):
    model_config = ConfigDict(extra="allow")

    written_by_triple: str
    written_at_step: int
    value_hash: str = ""
    derived_from: list[str] = Field(default_factory=list)


class ProvenanceLog(BaseModel):
    """Dict keyed by dotted state path → list of writes."""
    model_config = ConfigDict(extra="allow")

    entries: dict[str, list[ProvenanceEntry]] = Field(default_factory=dict)


class LLMInteractionRecord(BaseModel):
    model_config = ConfigDict(extra="allow")

    model: str = ""
    model_version: str = ""
    temperature: float = 0.0
    seed: int = 0
    prompt_template_version: str = ""
    prompt_sent: str = ""
    content_provided: list[str] = Field(default_factory=list)  # chunk_ids
    context_provided: dict = Field(default_factory=dict)
    raw_response: str = ""
    parsed_response: dict = Field(default_factory=dict)
    token_counts: dict = Field(default_factory=lambda: {"input": 0, "output": 0})
    refusals: list[dict] = Field(default_factory=list)


class NodeExecution(BaseModel):
    model_config = ConfigDict(extra="allow")

    step_index: int
    triple_id: str
    bpmn_node_id: str
    entered_at_state_hash: str = ""
    exited_at_state_hash: str = ""
    mode: ExecutionMode = ExecutionMode.STATIC
    duration_ms: int = 0
    state_reads_observed: list[StateFieldRef] = Field(default_factory=list)
    state_writes_observed: list[StateFieldRef] = Field(default_factory=list)
    obligations_opened: list[str] = Field(default_factory=list)
    obligations_closed: list[str] = Field(default_factory=list)
    branch_taken: Optional[str] = None
    branch_evidence: Optional[list[str]] = None
    llm_interaction: Optional[LLMInteractionRecord] = None
    findings_emitted: list[str] = Field(default_factory=list)


class OpenObligation(BaseModel):
    model_config = ConfigDict(extra="allow")

    obligation_id: str
    opened_at_step: int
    opened_by_triple: str
    must_close_by: Optional[dict] = None
    close_conditions: list[ContextAssertion] = Field(default_factory=list)


class ClosedObligation(BaseModel):
    model_config = ConfigDict(extra="allow")

    obligation_id: str
    closed_at_step: int
    closed_by_triple: str


class Attestation(BaseModel):
    model_config = ConfigDict(extra="allow")

    attestation_id: str
    attested_at_step: int
    attested_by_triple: str
    content: dict = Field(default_factory=dict)


class JourneyContext(BaseModel):
    """Mutable state object carried through a simulation.

    Spec reference: files/journey-context.md §Structure.
    """
    model_config = ConfigDict(extra="allow")

    journey_id: str
    persona_id: str = ""
    started_at: datetime = Field(default_factory=datetime.utcnow)
    current_node: str = ""
    corpus_version: str = ""
    journey_spec_version: str = ""

    state: dict = Field(default_factory=dict)
    provenance: ProvenanceLog = Field(default_factory=ProvenanceLog)
    history: list[NodeExecution] = Field(default_factory=list)
    open_obligations: list[OpenObligation] = Field(default_factory=list)
    closed_obligations: list[ClosedObligation] = Field(default_factory=list)
    attestations: list[Attestation] = Field(default_factory=list)
