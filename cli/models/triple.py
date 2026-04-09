"""Dataclasses for the three triple artifact types and their manifest."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class TripleStatus(str, Enum):
    DRAFT = "draft"
    REVIEW = "review"
    APPROVED = "approved"
    CURRENT = "current"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"


class GoalType(str, Enum):
    DATA_PRODUCTION = "data_production"
    DECISION = "decision"
    NOTIFICATION = "notification"
    STATE_TRANSITION = "state_transition"
    ORCHESTRATION = "orchestration"


class BindingStatus(str, Enum):
    UNBOUND = "unbound"
    PARTIAL = "partial"
    BOUND = "bound"


@dataclass
class CorpusRef:
    corpus_id: str
    section: str
    match_confidence: str

    def to_dict(self) -> dict:
        return {
            "corpus_id": self.corpus_id,
            "section": self.section,
            "match_confidence": self.match_confidence,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "CorpusRef":
        return cls(
            corpus_id=data["corpus_id"],
            section=data["section"],
            match_confidence=data["match_confidence"],
        )


@dataclass
class IntentInput:
    name: str
    source: str
    schema_ref: Optional[str] = None
    required: bool = True

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "source": self.source,
            "schema_ref": self.schema_ref,
            "required": self.required,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "IntentInput":
        return cls(
            name=data["name"],
            source=data["source"],
            schema_ref=data.get("schema_ref"),
            required=data.get("required", True),
        )


@dataclass
class IntentOutput:
    name: str
    type: str
    sink: str
    invariants: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "type": self.type,
            "sink": self.sink,
            "invariants": list(self.invariants),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "IntentOutput":
        return cls(
            name=data["name"],
            type=data["type"],
            sink=data["sink"],
            invariants=data.get("invariants", []),
        )


@dataclass
class FailureMode:
    mode: str
    detection: str
    action: str

    def to_dict(self) -> dict:
        return {
            "mode": self.mode,
            "detection": self.detection,
            "action": self.action,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "FailureMode":
        return cls(
            mode=data["mode"],
            detection=data["detection"],
            action=data["action"],
        )


@dataclass
class ExecutionHints:
    preferred_agent: Optional[str] = None
    tool_access: list[str] = field(default_factory=list)
    forbidden_actions: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "preferred_agent": self.preferred_agent,
            "tool_access": list(self.tool_access),
            "forbidden_actions": list(self.forbidden_actions),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ExecutionHints":
        return cls(
            preferred_agent=data.get("preferred_agent"),
            tool_access=data.get("tool_access", []),
            forbidden_actions=data.get("forbidden_actions", []),
        )


@dataclass
class ContractSource:
    name: str
    protocol: str
    endpoint: str
    auth: Optional[str] = None
    schema_ref: Optional[str] = None
    sla_ms: Optional[int] = None

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "protocol": self.protocol,
            "endpoint": self.endpoint,
            "auth": self.auth,
            "schema_ref": self.schema_ref,
            "sla_ms": self.sla_ms,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ContractSource":
        return cls(
            name=data["name"],
            protocol=data["protocol"],
            endpoint=data["endpoint"],
            auth=data.get("auth"),
            schema_ref=data.get("schema_ref"),
            sla_ms=data.get("sla_ms"),
        )


@dataclass
class ContractSink:
    name: str
    protocol: str
    endpoint: str
    auth: Optional[str] = None
    schema_ref: Optional[str] = None
    sla_ms: Optional[int] = None
    idempotency_key: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "protocol": self.protocol,
            "endpoint": self.endpoint,
            "auth": self.auth,
            "schema_ref": self.schema_ref,
            "sla_ms": self.sla_ms,
            "idempotency_key": self.idempotency_key,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ContractSink":
        return cls(
            name=data["name"],
            protocol=data["protocol"],
            endpoint=data["endpoint"],
            auth=data.get("auth"),
            schema_ref=data.get("schema_ref"),
            sla_ms=data.get("sla_ms"),
            idempotency_key=data.get("idempotency_key"),
        )


@dataclass
class ContractEvent:
    topic: str
    schema_ref: Optional[str] = None
    delivery: Optional[str] = None
    key_field: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "topic": self.topic,
            "schema_ref": self.schema_ref,
            "delivery": self.delivery,
            "key_field": self.key_field,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ContractEvent":
        return cls(
            topic=data["topic"],
            schema_ref=data.get("schema_ref"),
            delivery=data.get("delivery"),
            key_field=data.get("key_field"),
        )


@dataclass
class AuditConfig:
    record_type: str
    retention_years: int
    fields_required: list[str] = field(default_factory=list)
    sink: str = ""

    def to_dict(self) -> dict:
        return {
            "record_type": self.record_type,
            "retention_years": self.retention_years,
            "fields_required": list(self.fields_required),
            "sink": self.sink,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "AuditConfig":
        return cls(
            record_type=data["record_type"],
            retention_years=data["retention_years"],
            fields_required=data.get("fields_required", []),
            sink=data.get("sink", ""),
        )


@dataclass
class CapsuleFrontmatter:
    capsule_id: str
    bpmn_task_id: str
    bpmn_task_name: str
    bpmn_task_type: str
    process_id: str
    process_name: str
    version: str
    status: TripleStatus
    lane_id: Optional[str] = None
    lane_name: Optional[str] = None
    owner_role: Optional[str] = None
    owner_team: Optional[str] = None
    corpus_refs: list[CorpusRef] = field(default_factory=list)
    predecessor_ids: list[str] = field(default_factory=list)
    successor_ids: list[str] = field(default_factory=list)
    boundary_events: list[str] = field(default_factory=list)
    documentation: Optional[str] = None
    tags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "capsule_id": self.capsule_id,
            "bpmn_task_id": self.bpmn_task_id,
            "bpmn_task_name": self.bpmn_task_name,
            "bpmn_task_type": self.bpmn_task_type,
            "process_id": self.process_id,
            "process_name": self.process_name,
            "version": self.version,
            "status": self.status.value,
            "lane_id": self.lane_id,
            "lane_name": self.lane_name,
            "owner_role": self.owner_role,
            "owner_team": self.owner_team,
            "corpus_refs": [cr.to_dict() for cr in self.corpus_refs],
            "predecessor_ids": list(self.predecessor_ids),
            "successor_ids": list(self.successor_ids),
            "boundary_events": list(self.boundary_events),
            "documentation": self.documentation,
            "tags": list(self.tags),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "CapsuleFrontmatter":
        return cls(
            capsule_id=data["capsule_id"],
            bpmn_task_id=data["bpmn_task_id"],
            bpmn_task_name=data["bpmn_task_name"],
            bpmn_task_type=data["bpmn_task_type"],
            process_id=data["process_id"],
            process_name=data["process_name"],
            version=data["version"],
            status=TripleStatus(data["status"]),
            lane_id=data.get("lane_id"),
            lane_name=data.get("lane_name"),
            owner_role=data.get("owner_role"),
            owner_team=data.get("owner_team"),
            corpus_refs=[
                CorpusRef.from_dict(cr) for cr in data.get("corpus_refs", [])
            ],
            predecessor_ids=data.get("predecessor_ids", []),
            successor_ids=data.get("successor_ids", []),
            boundary_events=data.get("boundary_events", []),
            documentation=data.get("documentation"),
            tags=data.get("tags", []),
        )


@dataclass
class IntentFrontmatter:
    intent_id: str
    capsule_id: str
    bpmn_task_id: str
    version: str
    status: TripleStatus
    goal: str
    goal_type: GoalType
    inputs: list[IntentInput] = field(default_factory=list)
    outputs: list[IntentOutput] = field(default_factory=list)
    preconditions: list[str] = field(default_factory=list)
    postconditions: list[str] = field(default_factory=list)
    failure_modes: list[FailureMode] = field(default_factory=list)
    execution_hints: ExecutionHints = field(default_factory=ExecutionHints)
    corpus_refs: list[CorpusRef] = field(default_factory=list)
    decision_rules: list[dict] = field(default_factory=list)
    regulatory_refs: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "intent_id": self.intent_id,
            "capsule_id": self.capsule_id,
            "bpmn_task_id": self.bpmn_task_id,
            "version": self.version,
            "status": self.status.value,
            "goal": self.goal,
            "goal_type": self.goal_type.value,
            "inputs": [i.to_dict() for i in self.inputs],
            "outputs": [o.to_dict() for o in self.outputs],
            "preconditions": list(self.preconditions),
            "postconditions": list(self.postconditions),
            "failure_modes": [fm.to_dict() for fm in self.failure_modes],
            "execution_hints": self.execution_hints.to_dict(),
            "corpus_refs": [cr.to_dict() for cr in self.corpus_refs],
            "decision_rules": [dict(dr) for dr in self.decision_rules],
            "regulatory_refs": list(self.regulatory_refs),
            "tags": list(self.tags),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "IntentFrontmatter":
        return cls(
            intent_id=data["intent_id"],
            capsule_id=data["capsule_id"],
            bpmn_task_id=data["bpmn_task_id"],
            version=data["version"],
            status=TripleStatus(data["status"]),
            goal=data["goal"],
            goal_type=GoalType(data["goal_type"]),
            inputs=[IntentInput.from_dict(i) for i in data.get("inputs", [])],
            outputs=[IntentOutput.from_dict(o) for o in data.get("outputs", [])],
            preconditions=data.get("preconditions", []),
            postconditions=data.get("postconditions", []),
            failure_modes=[
                FailureMode.from_dict(fm) for fm in data.get("failure_modes", [])
            ],
            execution_hints=ExecutionHints.from_dict(
                data.get("execution_hints", {})
            ),
            corpus_refs=[
                CorpusRef.from_dict(cr) for cr in data.get("corpus_refs", [])
            ],
            decision_rules=data.get("decision_rules", []),
            regulatory_refs=data.get("regulatory_refs", []),
            tags=data.get("tags", []),
        )


@dataclass
class ContractFrontmatter:
    contract_id: str
    intent_id: str
    version: str
    status: TripleStatus
    binding_status: BindingStatus
    sources: list[ContractSource] = field(default_factory=list)
    sinks: list[ContractSink] = field(default_factory=list)
    events_published: list[ContractEvent] = field(default_factory=list)
    events_consumed: list[ContractEvent] = field(default_factory=list)
    audit: Optional[AuditConfig] = None
    sla_ms: Optional[int] = None
    retry_policy: Optional[dict] = None
    idempotency: Optional[dict] = None
    tags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "contract_id": self.contract_id,
            "intent_id": self.intent_id,
            "version": self.version,
            "status": self.status.value,
            "binding_status": self.binding_status.value,
            "sources": [s.to_dict() for s in self.sources],
            "sinks": [s.to_dict() for s in self.sinks],
            "events_published": [e.to_dict() for e in self.events_published],
            "events_consumed": [e.to_dict() for e in self.events_consumed],
            "audit": self.audit.to_dict() if self.audit is not None else None,
            "sla_ms": self.sla_ms,
            "retry_policy": dict(self.retry_policy) if self.retry_policy else None,
            "idempotency": dict(self.idempotency) if self.idempotency else None,
            "tags": list(self.tags),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ContractFrontmatter":
        audit_data = data.get("audit")
        return cls(
            contract_id=data["contract_id"],
            intent_id=data["intent_id"],
            version=data["version"],
            status=TripleStatus(data["status"]),
            binding_status=BindingStatus(data["binding_status"]),
            sources=[
                ContractSource.from_dict(s) for s in data.get("sources", [])
            ],
            sinks=[ContractSink.from_dict(s) for s in data.get("sinks", [])],
            events_published=[
                ContractEvent.from_dict(e)
                for e in data.get("events_published", [])
            ],
            events_consumed=[
                ContractEvent.from_dict(e)
                for e in data.get("events_consumed", [])
            ],
            audit=AuditConfig.from_dict(audit_data) if audit_data is not None else None,
            sla_ms=data.get("sla_ms"),
            retry_policy=data.get("retry_policy"),
            idempotency=data.get("idempotency"),
            tags=data.get("tags", []),
        )


@dataclass
class TripleManifest:
    triple_id: str
    capsule_id: str
    intent_id: str
    contract_id: str
    bpmn_task_id: str
    bpmn_process_id: str
    status: TripleStatus
    version: str
    created: str
    last_validated: Optional[str] = None
    validation_result: Optional[str] = None
    provenance: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "triple_id": self.triple_id,
            "capsule_id": self.capsule_id,
            "intent_id": self.intent_id,
            "contract_id": self.contract_id,
            "bpmn_task_id": self.bpmn_task_id,
            "bpmn_process_id": self.bpmn_process_id,
            "status": self.status.value,
            "version": self.version,
            "created": self.created,
            "last_validated": self.last_validated,
            "validation_result": self.validation_result,
            "provenance": dict(self.provenance),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "TripleManifest":
        return cls(
            triple_id=data["triple_id"],
            capsule_id=data["capsule_id"],
            intent_id=data["intent_id"],
            contract_id=data["contract_id"],
            bpmn_task_id=data["bpmn_task_id"],
            bpmn_process_id=data["bpmn_process_id"],
            status=TripleStatus(data["status"]),
            version=data["version"],
            created=data["created"],
            last_validated=data.get("last_validated"),
            validation_result=data.get("validation_result"),
            provenance=data.get("provenance", {}),
        )
