"""BPMN 2.0 XML parser.

Phase 1 scope: start_event, end_event, task (and specializations),
exclusive_gateway. Parallel gateways and intermediate events are parsed
into typed nodes but richer semantics are deferred.

Spec reference: files/03-journey-graph.md §B1
"""
from __future__ import annotations

import hashlib
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from triple_flow_sim.contracts import BpmnNodeType

BPMN_NS = "http://www.omg.org/spec/BPMN/20100524/MODEL"
NS = {"bpmn": BPMN_NS}

# -----------------------------------------------------------------------------
# Tag → node_type mapping
# -----------------------------------------------------------------------------
_TASK_TAGS = {
    "task",
    "userTask",
    "serviceTask",
    "businessRuleTask",
    "sendTask",
    "receiveTask",
    "manualTask",
    "scriptTask",
    "callActivity",
    "subProcess",
}
_GATEWAY_EXCLUSIVE_TAGS = {
    "exclusiveGateway",
    "inclusiveGateway",
    "eventBasedGateway",
    "complexGateway",
}
_GATEWAY_PARALLEL_TAGS = {"parallelGateway"}
_START_TAGS = {"startEvent"}
_END_TAGS = {"endEvent"}
_INTERMEDIATE_TAGS = {
    "intermediateCatchEvent",
    "intermediateThrowEvent",
    "boundaryEvent",
}

_ALL_NODE_TAGS = (
    _TASK_TAGS
    | _GATEWAY_EXCLUSIVE_TAGS
    | _GATEWAY_PARALLEL_TAGS
    | _START_TAGS
    | _END_TAGS
    | _INTERMEDIATE_TAGS
)

# ${ ... } wrapper stripper (handles leading/trailing whitespace).
_DOLLAR_BRACE_RE = re.compile(r"^\s*\$\{\s*(.*?)\s*\}\s*$", re.DOTALL)


# -----------------------------------------------------------------------------
# Data classes
# -----------------------------------------------------------------------------
@dataclass
class BpmnNodeDef:
    node_id: str
    node_type: BpmnNodeType
    name: str = ""
    lane: Optional[str] = None
    incoming: list[str] = field(default_factory=list)
    outgoing: list[str] = field(default_factory=list)


@dataclass
class BpmnEdgeDef:
    edge_id: str
    source: str
    target: str
    condition: Optional[str] = None
    is_default: bool = False
    name: Optional[str] = None


@dataclass
class BpmnGraphData:
    nodes: dict[str, BpmnNodeDef] = field(default_factory=dict)
    edges: dict[str, BpmnEdgeDef] = field(default_factory=dict)
    source_hash: str = ""


# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------
def _local(tag: str) -> str:
    """Strip XML namespace from a tag name."""
    if "}" in tag:
        return tag.split("}", 1)[1]
    return tag


def _classify(local_tag: str) -> Optional[BpmnNodeType]:
    if local_tag in _TASK_TAGS:
        return BpmnNodeType.TASK
    if local_tag in _GATEWAY_EXCLUSIVE_TAGS:
        return BpmnNodeType.EXCLUSIVE_GATEWAY
    if local_tag in _GATEWAY_PARALLEL_TAGS:
        return BpmnNodeType.PARALLEL_GATEWAY
    if local_tag in _START_TAGS:
        return BpmnNodeType.START_EVENT
    if local_tag in _END_TAGS:
        return BpmnNodeType.END_EVENT
    if local_tag in _INTERMEDIATE_TAGS:
        return BpmnNodeType.INTERMEDIATE_EVENT
    return None


def _strip_expr_wrapper(text: Optional[str]) -> Optional[str]:
    """Strip a ``${...}`` wrapper and/or outer whitespace from an expression.

    Also decodes XML entities that ElementTree leaves as raw characters in
    the body (the parser already handles standard entities, but whitespace
    trimming is ours to do).
    """
    if text is None:
        return None
    txt = text.strip()
    if not txt:
        return None
    m = _DOLLAR_BRACE_RE.match(txt)
    if m:
        txt = m.group(1).strip()
    return txt or None


def _collect_lane_map(root: ET.Element) -> dict[str, str]:
    """Return node_id -> lane_name for every flowNodeRef inside a lane."""
    out: dict[str, str] = {}
    for lane in root.iter(f"{{{BPMN_NS}}}lane"):
        lane_name = lane.get("name") or lane.get("id") or ""
        for ref in lane.findall(f"{{{BPMN_NS}}}flowNodeRef"):
            if ref.text and ref.text.strip():
                out[ref.text.strip()] = lane_name
    return out


def _find_process_default_edges(root: ET.Element) -> set[str]:
    """Return the set of sequenceFlow ids referenced as gateway/task `default`."""
    defaults: set[str] = set()
    # Any element with a 'default' attribute in BPMN is pointing at a flow id.
    for el in root.iter():
        default_id = el.get("default")
        if default_id:
            defaults.add(default_id)
    return defaults


# -----------------------------------------------------------------------------
# Public API
# -----------------------------------------------------------------------------
def parse_bpmn(path: Path) -> BpmnGraphData:
    """Parse a BPMN 2.0 XML file into typed nodes and edges.

    See files/03-journey-graph.md §B1. source_hash is the SHA-256 of the file
    content to support deterministic reproducibility checks.
    """
    path = Path(path)
    raw_bytes = path.read_bytes()
    source_hash = hashlib.sha256(raw_bytes).hexdigest()

    tree = ET.ElementTree(ET.fromstring(raw_bytes))
    root = tree.getroot()

    data = BpmnGraphData(source_hash=source_hash)

    lane_map = _collect_lane_map(root)
    default_flow_ids = _find_process_default_edges(root)

    # -------------------------------------------------------------------------
    # Pass 1: collect nodes.
    # -------------------------------------------------------------------------
    for el in root.iter():
        if not el.tag.startswith(f"{{{BPMN_NS}}}"):
            continue
        local = _local(el.tag)
        nt = _classify(local)
        if nt is None:
            continue
        node_id = el.get("id")
        if not node_id:
            continue
        node = BpmnNodeDef(
            node_id=node_id,
            node_type=nt,
            name=el.get("name", "") or "",
            lane=lane_map.get(node_id),
        )
        # Pick up <incoming>/<outgoing> child refs if present.
        for child in el:
            child_local = _local(child.tag)
            if child_local == "incoming" and child.text:
                node.incoming.append(child.text.strip())
            elif child_local == "outgoing" and child.text:
                node.outgoing.append(child.text.strip())
        data.nodes[node_id] = node

    # -------------------------------------------------------------------------
    # Pass 2: collect edges.
    # -------------------------------------------------------------------------
    for el in root.iter(f"{{{BPMN_NS}}}sequenceFlow"):
        edge_id = el.get("id")
        source = el.get("sourceRef", "")
        target = el.get("targetRef", "")
        if not edge_id or not source or not target:
            continue
        cond_text: Optional[str] = None
        for child in el:
            if _local(child.tag) == "conditionExpression":
                cond_text = _strip_expr_wrapper(
                    "".join(child.itertext())
                )
                break
        edge = BpmnEdgeDef(
            edge_id=edge_id,
            source=source,
            target=target,
            condition=cond_text,
            is_default=(edge_id in default_flow_ids),
            name=el.get("name"),
        )
        data.edges[edge_id] = edge

        # Back-fill incoming/outgoing on the node defs if they were not listed.
        if source in data.nodes and edge_id not in data.nodes[source].outgoing:
            data.nodes[source].outgoing.append(edge_id)
        if target in data.nodes and edge_id not in data.nodes[target].incoming:
            data.nodes[target].incoming.append(edge_id)

    return data
