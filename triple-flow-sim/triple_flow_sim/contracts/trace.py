"""Pydantic models for execution traces.

Spec reference: files/trace-schema.md

Note: Phase 1 builds these models for forward compatibility. Only the inventory
generator emits a minimal trace in Phase 1; full TraceStep population happens
in Phase 2 (static) and Phase 3 (grounded).
"""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field

from triple_flow_sim.contracts.journey_context import (
    JourneyContext,
    LLMInteractionRecord,
)
from triple_flow_sim.contracts.triple import ContextAssertion, StateFieldRef


class TraceMode(str, Enum):
    STATIC = "static"
    GROUNDED = "grounded"
    ISOLATED = "isolated"
    BRANCH_BOUNDARY = "branch_boundary"
    PERTURBATION = "perturbation"
    ABLATION = "ablation"
    INVENTORY = "inventory"


class TraceOutcome(str, Enum):
    COMPLETED = "completed"
    STUCK = "stuck"
    REGULATORY_VIOLATION = "regulatory_violation"
    LOOP_DETECTED = "loop_detected"
    ERROR = "error"
    REPORT_ONLY = "report_only"  # For inventory generator — no journey executed


class IsolationOutcome(str, Enum):
    SUCCESS = "success"
    PARTIAL = "partial"
    FAILURE = "failure"


class StateDiff(BaseModel):
    model_config = ConfigDict(extra="allow")

    added: dict = Field(default_factory=dict)
    modified: dict = Field(default_factory=dict)  # path -> {old_value, new_value}
    unchanged_but_read: list[str] = Field(default_factory=list)


class StaticResult(BaseModel):
    model_config = ConfigDict(extra="allow")

    preconditions_satisfied: list[dict] = Field(default_factory=list)
    postconditions_declared: list[ContextAssertion] = Field(default_factory=list)
    obligations_opened: list[str] = Field(default_factory=list)
    obligations_closed: list[str] = Field(default_factory=list)
    passed: bool = True
    failure_reasons: list[str] = Field(default_factory=list)


class DivergenceSignature(BaseModel):
    model_config = ConfigDict(extra="allow")

    missing_without_content: list[StateFieldRef] = Field(default_factory=list)
    extra_with_content: list[StateFieldRef] = Field(default_factory=list)
    behavior_change: str = ""


class IsolationResult(BaseModel):
    model_config = ConfigDict(extra="allow")

    full_content_outcome: IsolationOutcome = IsolationOutcome.SUCCESS
    declared_only_outcome: IsolationOutcome = IsolationOutcome.SUCCESS
    divergence: bool = False
    divergence_signature: Optional[DivergenceSignature] = None


class BranchEvaluationRecord(BaseModel):
    model_config = ConfigDict(extra="allow")

    predicates_evaluated: list[dict] = Field(default_factory=list)
    branch_taken: str = ""
    branch_agreed_between_static_and_grounded: Optional[bool] = None


class TraceStep(BaseModel):
    """One entry per triple execution. Spec: files/trace-schema.md §TraceStep."""
    model_config = ConfigDict(extra="allow")

    step_index: int
    triple_id: str
    triple_version: str = ""
    bpmn_node_id: str = ""
    bpmn_node_type: str = ""

    entered_at: datetime = Field(default_factory=datetime.utcnow)
    exited_at: datetime = Field(default_factory=datetime.utcnow)
    duration_ms: int = 0

    state_hash_in: str = ""
    state_hash_out: str = ""
    state_diff: StateDiff = Field(default_factory=StateDiff)

    declared_reads: list[StateFieldRef] = Field(default_factory=list)
    observed_reads: list[StateFieldRef] = Field(default_factory=list)
    declared_writes: list[StateFieldRef] = Field(default_factory=list)
    observed_writes: list[StateFieldRef] = Field(default_factory=list)

    static_evaluation: Optional[StaticResult] = None
    llm_interaction: Optional[LLMInteractionRecord] = None
    isolation_comparison: Optional[IsolationResult] = None

    branch_evaluation: Optional[BranchEvaluationRecord] = None

    findings: list[str] = Field(default_factory=list)


class GeneratorConfig(BaseModel):
    model_config = ConfigDict(extra="allow")

    persona_seed: int = 0
    perturbation_seed: Optional[int] = None
    mode: TraceMode = TraceMode.INVENTORY


class LLMConfig(BaseModel):
    model_config = ConfigDict(extra="allow")

    model: str = ""
    model_version: str = ""
    temperature: float = 0.0
    seed: int = 0
    prompt_template_version: str = ""


class TraceMetrics(BaseModel):
    model_config = ConfigDict(extra="allow")

    steps_executed: int = 0
    duration_ms: int = 0
    total_tokens_in: Optional[int] = None
    total_tokens_out: Optional[int] = None
    findings_count_by_class: dict = Field(default_factory=dict)
    obligations_opened: int = 0
    obligations_closed: int = 0
    obligations_unclosed: int = 0


class Persona(BaseModel):
    """Minimal persona model — full shape defined by component 09."""
    model_config = ConfigDict(extra="allow")

    persona_id: str = "inventory"
    description: str = "No persona — inventory run"
    seed_state: dict = Field(default_factory=dict)


class Trace(BaseModel):
    """Full trace record. Spec: files/trace-schema.md §Trace record."""
    model_config = ConfigDict(extra="allow")

    trace_id: str
    run_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    simulator_version: str = ""
    taxonomy_version: str = ""
    corpus_version: str = ""
    bpmn_version: str = ""
    generator_config: GeneratorConfig = Field(default_factory=GeneratorConfig)
    llm_config: Optional[LLMConfig] = None

    seed_context: Optional[JourneyContext] = None
    persona: Optional[Persona] = None

    steps: list[TraceStep] = Field(default_factory=list)

    outcome: TraceOutcome = TraceOutcome.REPORT_ONLY
    outcome_node: str = ""
    final_context: Optional[JourneyContext] = None

    metrics: TraceMetrics = Field(default_factory=TraceMetrics)

    finding_ids: list[str] = Field(default_factory=list)
