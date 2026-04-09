"""Dataclasses for Stage 1 BPMN parser output."""

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Optional


class BpmnTaskType(str, Enum):
    TASK = "task"
    USER_TASK = "userTask"
    SERVICE_TASK = "serviceTask"
    BUSINESS_RULE_TASK = "businessRuleTask"
    SEND_TASK = "sendTask"
    RECEIVE_TASK = "receiveTask"
    SCRIPT_TASK = "scriptTask"
    MANUAL_TASK = "manualTask"
    CALL_ACTIVITY = "callActivity"
    SUB_PROCESS = "subProcess"


class BpmnGatewayType(str, Enum):
    EXCLUSIVE = "exclusiveGateway"
    INCLUSIVE = "inclusiveGateway"
    PARALLEL = "parallelGateway"
    EVENT_BASED = "eventBasedGateway"


class BpmnEventType(str, Enum):
    START = "startEvent"
    END = "endEvent"
    INTERMEDIATE_CATCH = "intermediateCatchEvent"
    INTERMEDIATE_THROW = "intermediateThrowEvent"
    BOUNDARY = "boundaryEvent"


class BpmnElementType(str, Enum):
    """All BPMN element types that can appear as nodes."""
    # Task types
    TASK = "task"
    USER_TASK = "userTask"
    SERVICE_TASK = "serviceTask"
    BUSINESS_RULE_TASK = "businessRuleTask"
    SEND_TASK = "sendTask"
    RECEIVE_TASK = "receiveTask"
    SCRIPT_TASK = "scriptTask"
    MANUAL_TASK = "manualTask"
    CALL_ACTIVITY = "callActivity"
    SUB_PROCESS = "subProcess"
    # Gateway types
    EXCLUSIVE_GATEWAY = "exclusiveGateway"
    INCLUSIVE_GATEWAY = "inclusiveGateway"
    PARALLEL_GATEWAY = "parallelGateway"
    EVENT_BASED_GATEWAY = "eventBasedGateway"
    # Event types
    START_EVENT = "startEvent"
    END_EVENT = "endEvent"
    INTERMEDIATE_CATCH_EVENT = "intermediateCatchEvent"
    INTERMEDIATE_THROW_EVENT = "intermediateThrowEvent"
    BOUNDARY_EVENT = "boundaryEvent"


@dataclass
class BpmnNode:
    id: str
    name: Optional[str]
    element_type: str  # The raw BPMN type string (e.g., "serviceTask")
    lane_id: Optional[str] = None
    lane_name: Optional[str] = None
    incoming: list[str] = field(default_factory=list)  # edge IDs
    outgoing: list[str] = field(default_factory=list)
    boundary_event_ids: list[str] = field(default_factory=list)
    attached_to: Optional[str] = None  # For boundary events
    documentation: Optional[str] = None
    attributes: dict = field(default_factory=dict)  # BPMN-specific attrs
    event_definitions: list[dict] = field(default_factory=list)
    gateway_direction: Optional[str] = None  # converging, diverging, mixed
    default_flow: Optional[str] = None  # default sequence flow for gateways

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "element_type": self.element_type,
            "lane_id": self.lane_id,
            "lane_name": self.lane_name,
            "incoming": list(self.incoming),
            "outgoing": list(self.outgoing),
            "boundary_event_ids": list(self.boundary_event_ids),
            "attached_to": self.attached_to,
            "documentation": self.documentation,
            "attributes": dict(self.attributes),
            "event_definitions": [dict(d) for d in self.event_definitions],
            "gateway_direction": self.gateway_direction,
            "default_flow": self.default_flow,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "BpmnNode":
        return cls(
            id=data["id"],
            name=data.get("name"),
            element_type=data["element_type"],
            lane_id=data.get("lane_id"),
            lane_name=data.get("lane_name"),
            incoming=data.get("incoming", []),
            outgoing=data.get("outgoing", []),
            boundary_event_ids=data.get("boundary_event_ids", []),
            attached_to=data.get("attached_to"),
            documentation=data.get("documentation"),
            attributes=data.get("attributes", {}),
            event_definitions=data.get("event_definitions", []),
            gateway_direction=data.get("gateway_direction"),
            default_flow=data.get("default_flow"),
        )


@dataclass
class BpmnEdge:
    id: str
    source_id: str
    target_id: str
    name: Optional[str] = None
    condition_expression: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "source_id": self.source_id,
            "target_id": self.target_id,
            "name": self.name,
            "condition_expression": self.condition_expression,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "BpmnEdge":
        return cls(
            id=data["id"],
            source_id=data["source_id"],
            target_id=data["target_id"],
            name=data.get("name"),
            condition_expression=data.get("condition_expression"),
        )


@dataclass
class BpmnLane:
    id: str
    name: Optional[str]
    node_ids: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "node_ids": list(self.node_ids),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "BpmnLane":
        return cls(
            id=data["id"],
            name=data.get("name"),
            node_ids=data.get("node_ids", []),
        )


@dataclass
class BpmnDataObject:
    id: str
    name: Optional[str]
    item_subject_ref: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "item_subject_ref": self.item_subject_ref,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "BpmnDataObject":
        return cls(
            id=data["id"],
            name=data.get("name"),
            item_subject_ref=data.get("item_subject_ref"),
        )


@dataclass
class BpmnDataAssociation:
    id: str
    source_ref: str
    target_ref: str

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "source_ref": self.source_ref,
            "target_ref": self.target_ref,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "BpmnDataAssociation":
        return cls(
            id=data["id"],
            source_ref=data["source_ref"],
            target_ref=data["target_ref"],
        )


@dataclass
class BpmnMessageFlow:
    id: str
    source_ref: str
    target_ref: str
    name: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "source_ref": self.source_ref,
            "target_ref": self.target_ref,
            "name": self.name,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "BpmnMessageFlow":
        return cls(
            id=data["id"],
            source_ref=data["source_ref"],
            target_ref=data["target_ref"],
            name=data.get("name"),
        )


@dataclass
class BpmnProcess:
    id: str
    name: Optional[str]
    is_executable: bool = False

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "is_executable": self.is_executable,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "BpmnProcess":
        return cls(
            id=data["id"],
            name=data.get("name"),
            is_executable=data.get("is_executable", False),
        )


@dataclass
class ParsedModel:
    """Complete output of Stage 1 parser."""
    processes: list[BpmnProcess] = field(default_factory=list)
    nodes: list[BpmnNode] = field(default_factory=list)
    edges: list[BpmnEdge] = field(default_factory=list)
    lanes: list[BpmnLane] = field(default_factory=list)
    data_objects: list[BpmnDataObject] = field(default_factory=list)
    data_associations: list[BpmnDataAssociation] = field(default_factory=list)
    message_flows: list[BpmnMessageFlow] = field(default_factory=list)
    source_file: Optional[str] = None

    def get_node(self, node_id: str) -> Optional[BpmnNode]:
        """Find a node by its ID."""
        for node in self.nodes:
            if node.id == node_id:
                return node
        return None

    def get_edge(self, edge_id: str) -> Optional[BpmnEdge]:
        """Find an edge by its ID."""
        for edge in self.edges:
            if edge.id == edge_id:
                return edge
        return None

    def get_predecessors(self, node_id: str) -> list[BpmnNode]:
        """Get all nodes that have edges pointing to this node."""
        source_ids = [
            edge.source_id for edge in self.edges if edge.target_id == node_id
        ]
        return [node for node in self.nodes if node.id in source_ids]

    def get_successors(self, node_id: str) -> list[BpmnNode]:
        """Get all nodes this node has edges pointing to."""
        target_ids = [
            edge.target_id for edge in self.edges if edge.source_id == node_id
        ]
        return [node for node in self.nodes if node.id in target_ids]

    def get_lane_for_node(self, node_id: str) -> Optional[BpmnLane]:
        """Find the lane that contains a given node."""
        for lane in self.lanes:
            if node_id in lane.node_ids:
                return lane
        return None

    def to_dict(self) -> dict:
        """Serialize to a dict suitable for YAML/JSON output."""
        return {
            "processes": [p.to_dict() for p in self.processes],
            "nodes": [n.to_dict() for n in self.nodes],
            "edges": [e.to_dict() for e in self.edges],
            "lanes": [l.to_dict() for l in self.lanes],
            "data_objects": [d.to_dict() for d in self.data_objects],
            "data_associations": [da.to_dict() for da in self.data_associations],
            "message_flows": [mf.to_dict() for mf in self.message_flows],
            "source_file": self.source_file,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ParsedModel":
        """Deserialize from a dict."""
        return cls(
            processes=[
                BpmnProcess.from_dict(p) for p in data.get("processes", [])
            ],
            nodes=[BpmnNode.from_dict(n) for n in data.get("nodes", [])],
            edges=[BpmnEdge.from_dict(e) for e in data.get("edges", [])],
            lanes=[BpmnLane.from_dict(l) for l in data.get("lanes", [])],
            data_objects=[
                BpmnDataObject.from_dict(d) for d in data.get("data_objects", [])
            ],
            data_associations=[
                BpmnDataAssociation.from_dict(da)
                for da in data.get("data_associations", [])
            ],
            message_flows=[
                BpmnMessageFlow.from_dict(mf)
                for mf in data.get("message_flows", [])
            ],
            source_file=data.get("source_file"),
        )
