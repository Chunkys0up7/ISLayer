"""Parse BPMN 2.0 XML files using stdlib xml.etree.ElementTree."""

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Optional
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.bpmn import (
    ParsedModel,
    BpmnProcess,
    BpmnNode,
    BpmnEdge,
    BpmnLane,
    BpmnDataObject,
    BpmnDataAssociation,
    BpmnMessageFlow,
)

# BPMN 2.0 namespace
BPMN_NS = "http://www.omg.org/spec/BPMN/20100524/MODEL"
BPMNDI_NS = "http://www.omg.org/spec/BPMN/20100524/DI"

# All BPMN task types that produce nodes
TASK_TAGS = [
    "task",
    "userTask",
    "serviceTask",
    "businessRuleTask",
    "sendTask",
    "receiveTask",
    "scriptTask",
    "manualTask",
    "callActivity",
    "subProcess",
]

GATEWAY_TAGS = [
    "exclusiveGateway",
    "inclusiveGateway",
    "parallelGateway",
    "eventBasedGateway",
]

EVENT_TAGS = [
    "startEvent",
    "endEvent",
    "intermediateCatchEvent",
    "intermediateThrowEvent",
    "boundaryEvent",
]

ALL_NODE_TAGS = TASK_TAGS + GATEWAY_TAGS + EVENT_TAGS

# Counter for generating synthetic IDs
_synthetic_id_counter = 0


def _next_synthetic_id(prefix: str = "synth") -> str:
    """Generate a synthetic ID for elements without an id attribute."""
    global _synthetic_id_counter
    _synthetic_id_counter += 1
    return f"{prefix}_{_synthetic_id_counter}"


def _reset_synthetic_ids() -> None:
    """Reset the synthetic ID counter (useful for testing)."""
    global _synthetic_id_counter
    _synthetic_id_counter = 0


def _ns(tag: str) -> str:
    """Prepend the BPMN namespace to a tag name."""
    return f"{{{BPMN_NS}}}{tag}"


def _local_tag(element: ET.Element) -> str:
    """Extract the local tag name, stripping any namespace prefix."""
    tag = element.tag
    if "}" in tag:
        return tag.split("}", 1)[1]
    return tag


def parse_bpmn(path: Path) -> ParsedModel:
    """Parse a BPMN 2.0 XML file into a ParsedModel.

    Steps:
    1. Parse XML and validate BPMN namespace
    2. Extract process definitions
    3. Extract all nodes (tasks, gateways, events) from each process
    4. Extract sequence flows as edges
    5. Extract lane sets and assign nodes to lanes
    6. Extract data objects and data stores
    7. Extract data associations
    8. Extract message flows from collaboration elements
    9. Handle boundary events (link to parent task via attachedToRef)
    10. Generate synthetic IDs for elements without IDs
    """
    _reset_synthetic_ids()

    tree = ET.parse(str(path))
    root = tree.getroot()

    # Validate BPMN namespace
    if not root.tag.startswith(f"{{{BPMN_NS}}}"):
        raise ValueError(f"Not a valid BPMN 2.0 file: root tag is {root.tag}")

    model = ParsedModel(source_file=str(path))

    # Extract processes
    model.processes = _extract_processes(root)

    # Extract nodes, edges, lanes, data objects, and associations per process
    for process_elem in root.findall(_ns("process")):
        model.nodes.extend(_extract_nodes(process_elem))
        model.edges.extend(_extract_edges(process_elem))
        model.lanes.extend(_extract_lanes(process_elem))
        model.data_objects.extend(_extract_data_objects(process_elem))
        model.data_associations.extend(_extract_data_associations(process_elem))

    # Extract message flows from collaboration elements
    model.message_flows = _extract_message_flows(root)

    # Post-processing: assign lane info to nodes
    _assign_lanes_to_nodes(model)

    # Post-processing: link boundary events to parent tasks
    _link_boundary_events(model)

    # Post-processing: populate incoming/outgoing on nodes from edges
    _populate_node_flows(model)

    return model


def _extract_processes(root: ET.Element) -> list[BpmnProcess]:
    """Extract all <process> elements."""
    processes = []
    for proc_elem in root.findall(_ns("process")):
        proc_id = proc_elem.get("id") or _next_synthetic_id("process")
        name = proc_elem.get("name")
        is_executable = proc_elem.get("isExecutable", "false").lower() == "true"
        processes.append(
            BpmnProcess(id=proc_id, name=name, is_executable=is_executable)
        )
    return processes


def _extract_nodes(process_elem: ET.Element) -> list[BpmnNode]:
    """Extract all task, gateway, and event nodes from a process."""
    nodes = []

    for tag in ALL_NODE_TAGS:
        for elem in process_elem.findall(_ns(tag)):
            node_id = elem.get("id") or _next_synthetic_id(tag)
            name = elem.get("name")

            node = BpmnNode(
                id=node_id,
                name=name,
                element_type=tag,
            )

            # Gateway-specific attributes
            if tag in GATEWAY_TAGS:
                node.gateway_direction = elem.get("gatewayDirection")
                node.default_flow = elem.get("default")

            # Boundary event: capture attachedToRef
            if tag == "boundaryEvent":
                node.attached_to = elem.get("attachedToRef")
                cancel = elem.get("cancelActivity", "true")
                node.attributes["cancel_activity"] = cancel.lower() == "true"

            # Extract documentation
            doc_elem = elem.find(_ns("documentation"))
            if doc_elem is not None and doc_elem.text:
                node.documentation = doc_elem.text.strip()

            # Extract event definitions (timer, message, signal, error, etc.)
            node.event_definitions = _extract_event_definitions(elem)

            nodes.append(node)

    return nodes


def _extract_edges(process_elem: ET.Element) -> list[BpmnEdge]:
    """Extract all sequenceFlow elements."""
    edges = []
    for flow_elem in process_elem.findall(_ns("sequenceFlow")):
        flow_id = flow_elem.get("id") or _next_synthetic_id("flow")
        source_id = flow_elem.get("sourceRef", "")
        target_id = flow_elem.get("targetRef", "")
        name = flow_elem.get("name")

        # Extract condition expression
        condition_expression = None
        cond_elem = flow_elem.find(_ns("conditionExpression"))
        if cond_elem is not None and cond_elem.text:
            condition_expression = cond_elem.text.strip()

        edges.append(
            BpmnEdge(
                id=flow_id,
                source_id=source_id,
                target_id=target_id,
                name=name,
                condition_expression=condition_expression,
            )
        )
    return edges


def _extract_lanes(process_elem: ET.Element) -> list[BpmnLane]:
    """Extract laneSet/lane elements."""
    lanes = []
    for lane_set in process_elem.findall(_ns("laneSet")):
        for lane_elem in lane_set.findall(_ns("lane")):
            lane_id = lane_elem.get("id") or _next_synthetic_id("lane")
            name = lane_elem.get("name")

            node_ids = []
            for ref_elem in lane_elem.findall(_ns("flowNodeRef")):
                if ref_elem.text:
                    node_ids.append(ref_elem.text.strip())

            lanes.append(BpmnLane(id=lane_id, name=name, node_ids=node_ids))
    return lanes


def _extract_data_objects(process_elem: ET.Element) -> list[BpmnDataObject]:
    """Extract dataObject and dataStoreReference elements."""
    data_objects = []

    for tag in ("dataObject", "dataStoreReference", "dataObjectReference"):
        for elem in process_elem.findall(_ns(tag)):
            obj_id = elem.get("id") or _next_synthetic_id("data")
            name = elem.get("name")
            item_ref = elem.get("itemSubjectRef")
            data_objects.append(
                BpmnDataObject(id=obj_id, name=name, item_subject_ref=item_ref)
            )

    return data_objects


def _extract_data_associations(
    process_elem: ET.Element,
) -> list[BpmnDataAssociation]:
    """Extract dataInputAssociation and dataOutputAssociation elements.

    These are nested inside task elements, so we walk all node elements.
    """
    associations = []

    for tag in ALL_NODE_TAGS:
        for node_elem in process_elem.findall(_ns(tag)):
            node_id = node_elem.get("id", "")

            # Data input associations: source -> this node
            for dia in node_elem.findall(_ns("dataInputAssociation")):
                assoc_id = dia.get("id") or _next_synthetic_id("dia")
                source_elem = dia.find(_ns("sourceRef"))
                source_ref = (
                    source_elem.text.strip()
                    if source_elem is not None and source_elem.text
                    else ""
                )
                associations.append(
                    BpmnDataAssociation(
                        id=assoc_id,
                        source_ref=source_ref,
                        target_ref=node_id,
                    )
                )

            # Data output associations: this node -> target
            for doa in node_elem.findall(_ns("dataOutputAssociation")):
                assoc_id = doa.get("id") or _next_synthetic_id("doa")
                target_elem = doa.find(_ns("targetRef"))
                target_ref = (
                    target_elem.text.strip()
                    if target_elem is not None and target_elem.text
                    else ""
                )
                associations.append(
                    BpmnDataAssociation(
                        id=assoc_id,
                        source_ref=node_id,
                        target_ref=target_ref,
                    )
                )

    return associations


def _extract_message_flows(root: ET.Element) -> list[BpmnMessageFlow]:
    """Extract messageFlow elements from collaboration."""
    message_flows = []

    for collab in root.findall(_ns("collaboration")):
        for mf_elem in collab.findall(_ns("messageFlow")):
            mf_id = mf_elem.get("id") or _next_synthetic_id("msgflow")
            source_ref = mf_elem.get("sourceRef", "")
            target_ref = mf_elem.get("targetRef", "")
            name = mf_elem.get("name")

            message_flows.append(
                BpmnMessageFlow(
                    id=mf_id,
                    source_ref=source_ref,
                    target_ref=target_ref,
                    name=name,
                )
            )

    return message_flows


def _extract_event_definitions(element: ET.Element) -> list[dict]:
    """Extract timer, message, signal, error event definitions."""
    definitions = []

    event_def_tags = [
        "timerEventDefinition",
        "messageEventDefinition",
        "signalEventDefinition",
        "errorEventDefinition",
        "escalationEventDefinition",
        "compensateEventDefinition",
        "conditionalEventDefinition",
        "linkEventDefinition",
        "terminateEventDefinition",
        "cancelEventDefinition",
    ]

    for def_tag in event_def_tags:
        for def_elem in element.findall(_ns(def_tag)):
            event_def: dict = {
                "type": def_tag.replace("EventDefinition", ""),
            }

            def_id = def_elem.get("id")
            if def_id:
                event_def["id"] = def_id

            # Timer-specific children
            if def_tag == "timerEventDefinition":
                for child_tag in ("timeDuration", "timeDate", "timeCycle"):
                    child = def_elem.find(_ns(child_tag))
                    if child is not None and child.text:
                        event_def[child_tag] = child.text.strip()

            # Message/Signal/Error refs
            for ref_attr in ("messageRef", "signalRef", "errorRef", "escalationRef"):
                ref_val = def_elem.get(ref_attr)
                if ref_val:
                    event_def[ref_attr] = ref_val

            definitions.append(event_def)

    return definitions


def _assign_lanes_to_nodes(model: ParsedModel) -> None:
    """Set lane_id and lane_name on each node based on lane membership."""
    for lane in model.lanes:
        for node_id in lane.node_ids:
            node = model.get_node(node_id)
            if node is not None:
                node.lane_id = lane.id
                node.lane_name = lane.name


def _link_boundary_events(model: ParsedModel) -> None:
    """Link boundary events to their parent tasks via attachedToRef."""
    for node in model.nodes:
        if node.element_type == "boundaryEvent" and node.attached_to:
            parent = model.get_node(node.attached_to)
            if parent is not None:
                parent.boundary_event_ids.append(node.id)


def _populate_node_flows(model: ParsedModel) -> None:
    """Populate incoming/outgoing edge ID lists on each node from the edge data."""
    for edge in model.edges:
        source_node = model.get_node(edge.source_id)
        if source_node is not None:
            source_node.outgoing.append(edge.id)

        target_node = model.get_node(edge.target_id)
        if target_node is not None:
            target_node.incoming.append(edge.id)
