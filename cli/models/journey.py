"""Journey data models — process journey map, step summaries, and data lineage."""
from dataclasses import dataclass, field
from typing import Optional, Any


@dataclass
class InputSummary:
    name: str
    source: str
    schema_ref: Optional[str] = None
    required: bool = True

    def to_dict(self):
        return {"name": self.name, "source": self.source, "schema_ref": self.schema_ref, "required": self.required}

@dataclass
class OutputSummary:
    name: str
    type: str
    sink: str
    invariants: list[str] = field(default_factory=list)

    def to_dict(self):
        return {"name": self.name, "type": self.type, "sink": self.sink, "invariants": self.invariants}

@dataclass
class StepSummary:
    step_number: int
    capsule_id: str
    name: str
    task_type: str
    owner: Optional[str]

    preconditions: list[str] = field(default_factory=list)
    required_inputs: list[InputSummary] = field(default_factory=list)
    predecessor_steps: list[str] = field(default_factory=list)

    outputs: list[OutputSummary] = field(default_factory=list)
    invariants: list[str] = field(default_factory=list)
    events_emitted: list[str] = field(default_factory=list)
    successor_steps: list[str] = field(default_factory=list)

    sources: list[str] = field(default_factory=list)  # External system names
    sinks: list[str] = field(default_factory=list)

    jobaid_id: Optional[str] = None
    jobaid_dimensions: list[str] = field(default_factory=list)
    jobaid_rule_count: int = 0

    health_score: float = 0.0
    gaps: list[dict] = field(default_factory=list)
    binding_status: str = "unknown"

    slug: str = ""
    section: str = "tasks"

    def to_dict(self):
        return {
            "step_number": self.step_number,
            "capsule_id": self.capsule_id,
            "name": self.name,
            "task_type": self.task_type,
            "owner": self.owner,
            "preconditions": self.preconditions,
            "required_inputs": [i.to_dict() for i in self.required_inputs],
            "predecessor_steps": self.predecessor_steps,
            "outputs": [o.to_dict() for o in self.outputs],
            "invariants": self.invariants,
            "events_emitted": self.events_emitted,
            "successor_steps": self.successor_steps,
            "sources": self.sources,
            "sinks": self.sinks,
            "jobaid_id": self.jobaid_id,
            "jobaid_dimensions": self.jobaid_dimensions,
            "jobaid_rule_count": self.jobaid_rule_count,
            "health_score": round(self.health_score, 1),
            "gaps": self.gaps,
            "binding_status": self.binding_status,
            "slug": self.slug,
            "section": self.section,
        }


@dataclass
class DataLineage:
    data_name: str
    source: str  # "external" or capsule_id
    source_name: str  # human-readable
    consumers: list[dict] = field(default_factory=list)  # [{capsule_id, name}]

    def to_dict(self):
        return {"data_name": self.data_name, "source": self.source, "source_name": self.source_name, "consumers": self.consumers}


@dataclass
class BranchPoint:
    gateway_capsule_id: str
    gateway_name: str
    branches: list[dict] = field(default_factory=list)  # [{condition, target_capsule_id, target_name}]

    def to_dict(self):
        return {"gateway_capsule_id": self.gateway_capsule_id, "gateway_name": self.gateway_name, "branches": self.branches}


@dataclass
class ProcessJourney:
    process_name: str
    process_id: str
    total_steps: int
    steps: list[StepSummary] = field(default_factory=list)
    data_lineage: list[DataLineage] = field(default_factory=list)
    critical_path: list[str] = field(default_factory=list)
    branch_points: list[BranchPoint] = field(default_factory=list)
    health_summary: dict = field(default_factory=dict)

    def get_step(self, capsule_id: str) -> Optional[StepSummary]:
        for s in self.steps:
            if s.capsule_id == capsule_id:
                return s
        return None

    def get_data(self, data_name: str) -> Optional[DataLineage]:
        name_lower = data_name.lower().replace("-", "_").replace(" ", "_")
        for dl in self.data_lineage:
            if dl.data_name.lower().replace("-", "_").replace(" ", "_") == name_lower:
                return dl
        return None

    def to_dict(self):
        return {
            "process_name": self.process_name,
            "process_id": self.process_id,
            "total_steps": self.total_steps,
            "steps": [s.to_dict() for s in self.steps],
            "data_lineage": [dl.to_dict() for dl in self.data_lineage],
            "critical_path": self.critical_path,
            "branch_points": [bp.to_dict() for bp in self.branch_points],
            "health_summary": self.health_summary,
        }
