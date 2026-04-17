"""Tests for parallel-gateway handling.

Parallel gateways split into multiple concurrent branches — every outgoing
edge is taken. The graph must not reject such BPMNs, and traversal must reach
every branch.
"""
from __future__ import annotations

import pytest

from triple_flow_sim.components.c03_graph import JourneyGraph
from triple_flow_sim.components.c03_graph.bpmn_parser import (
    BpmnEdgeDef,
    BpmnGraphData,
    BpmnNodeDef,
)
from triple_flow_sim.contracts import BpmnNodeType, TripleSet


def _make_parallel_split_bpmn() -> BpmnGraphData:
    """start → PG_split → {A, B} → PG_join → end."""
    data = BpmnGraphData()
    data.nodes["start"] = BpmnNodeDef(
        node_id="start", node_type=BpmnNodeType.START_EVENT, name="Start"
    )
    data.nodes["pg_split"] = BpmnNodeDef(
        node_id="pg_split",
        node_type=BpmnNodeType.PARALLEL_GATEWAY,
        name="Split",
    )
    data.nodes["task_a"] = BpmnNodeDef(
        node_id="task_a", node_type=BpmnNodeType.TASK, name="A"
    )
    data.nodes["task_b"] = BpmnNodeDef(
        node_id="task_b", node_type=BpmnNodeType.TASK, name="B"
    )
    data.nodes["pg_join"] = BpmnNodeDef(
        node_id="pg_join",
        node_type=BpmnNodeType.PARALLEL_GATEWAY,
        name="Join",
    )
    data.nodes["end"] = BpmnNodeDef(
        node_id="end", node_type=BpmnNodeType.END_EVENT, name="End"
    )
    for eid, src, tgt in [
        ("e1", "start", "pg_split"),
        ("e2", "pg_split", "task_a"),
        ("e3", "pg_split", "task_b"),
        ("e4", "task_a", "pg_join"),
        ("e5", "task_b", "pg_join"),
        ("e6", "pg_join", "end"),
    ]:
        data.edges[eid] = BpmnEdgeDef(edge_id=eid, source=src, target=tgt)
    return data


def test_parallel_gateway_classified() -> None:
    data = _make_parallel_split_bpmn()
    g = JourneyGraph(data, TripleSet(triples={}))
    assert g.get_node("pg_split")["node_type"] == BpmnNodeType.PARALLEL_GATEWAY
    assert g.get_node("pg_join")["node_type"] == BpmnNodeType.PARALLEL_GATEWAY


def test_parallel_gateway_both_branches_reachable() -> None:
    data = _make_parallel_split_bpmn()
    g = JourneyGraph(data, TripleSet(triples={}))
    assert g.is_reachable("start", "task_a")
    assert g.is_reachable("start", "task_b")
    assert g.is_reachable("task_a", "end")
    assert g.is_reachable("task_b", "end")


def test_parallel_gateway_no_dead_end_detection() -> None:
    """Parallel gateways join/split should not be reported as dead ends."""
    data = _make_parallel_split_bpmn()
    g = JourneyGraph(data, TripleSet(triples={}))
    signals = [d.signal_type for d in g.detections]
    # No orphan_triple dead-end detections because gateway nodes are
    # unbound (no triple) and the checker skips them.
    for d in g.detections:
        assert d.detector_context.get("reason") != "dead_end" or (
            d.primary_triple_id is not None
        )


def test_parallel_gateway_outgoing_edges_enumerated() -> None:
    data = _make_parallel_split_bpmn()
    g = JourneyGraph(data, TripleSet(triples={}))
    edges = g.edges_from("pg_split")
    targets = sorted(e["target"] for e in edges)
    assert targets == ["task_a", "task_b"]
