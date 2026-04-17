"""Pydantic contract models for the Triple Flow Simulator.

Each submodule mirrors a spec file in ../files/:
- triple.py        ← triple-schema.md
- finding.py       ← finding-schema.md
- trace.py         ← trace-schema.md
- journey_context.py ← journey-context.md
"""

from triple_flow_sim.contracts.triple import (
    AssertionPredicate, BpmnNodeType, BranchPredicate, BusinessRule,
    CIMLayer, ContentChunk, ContentType, ContextAssertion, LoadReport,
    MustCloseBy, ObligationSpec, ObligationType, PIMLayer, PSMLayer,
    RegulatoryRef, StateFieldRef, ToolRef, Triple, TripleSet,
)
from triple_flow_sim.contracts.finding import (
    Confidence, DefectClass, Evidence, Finding, FindingStatus,
    Generator, Layer, RawDetection, Severity,
)
from triple_flow_sim.contracts.journey_context import (
    Attestation, ClosedObligation, ExecutionMode, JourneyContext,
    LLMInteractionRecord, NodeExecution, OpenObligation,
    ProvenanceEntry, ProvenanceLog,
)
from triple_flow_sim.contracts.trace import (
    BranchEvaluationRecord, DivergenceSignature, GeneratorConfig,
    IsolationOutcome, IsolationResult, LLMConfig, Persona,
    StateDiff, StaticResult, Trace, TraceMetrics, TraceMode,
    TraceOutcome, TraceStep,
)

__all__ = [
    "AssertionPredicate", "BpmnNodeType", "BranchPredicate", "BusinessRule",
    "CIMLayer", "ContentChunk", "ContentType", "ContextAssertion", "LoadReport",
    "MustCloseBy", "ObligationSpec", "ObligationType", "PIMLayer", "PSMLayer",
    "RegulatoryRef", "StateFieldRef", "ToolRef", "Triple", "TripleSet",
    "Confidence", "DefectClass", "Evidence", "Finding", "FindingStatus",
    "Generator", "Layer", "RawDetection", "Severity",
    "Attestation", "ClosedObligation", "ExecutionMode", "JourneyContext",
    "LLMInteractionRecord", "NodeExecution", "OpenObligation",
    "ProvenanceEntry", "ProvenanceLog",
    "BranchEvaluationRecord", "DivergenceSignature", "GeneratorConfig",
    "IsolationOutcome", "IsolationResult", "LLMConfig", "Persona",
    "StateDiff", "StaticResult", "Trace", "TraceMetrics", "TraceMode",
    "TraceOutcome", "TraceStep",
]
