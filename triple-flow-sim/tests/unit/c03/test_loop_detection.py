"""Tests for loop / cycle detection (files/03-journey-graph.md §B6)."""
from __future__ import annotations

import networkx as nx

from triple_flow_sim.components.c03_graph import JourneyGraph
from triple_flow_sim.components.c03_graph.bpmn_parser import (
    BpmnEdgeDef,
    BpmnGraphData,
    BpmnNodeDef,
)
from triple_flow_sim.components.c03_graph.loop_detection import (
    analyze_loop_termination,
    find_loops,
)
from triple_flow_sim.contracts import BpmnNodeType, TripleSet


def _make_unbounded_cycle() -> BpmnGraphData:
    """start → A → B → C → A (no exit gateway)."""
    data = BpmnGraphData()
    data.nodes["start"] = BpmnNodeDef(
        node_id="start", node_type=BpmnNodeType.START_EVENT
    )
    for t in ("a", "b", "c"):
        data.nodes[t] = BpmnNodeDef(node_id=t, node_type=BpmnNodeType.TASK)
    for eid, src, tgt in [
        ("e0", "start", "a"),
        ("e1", "a", "b"),
        ("e2", "b", "c"),
        ("e3", "c", "a"),
    ]:
        data.edges[eid] = BpmnEdgeDef(edge_id=eid, source=src, target=tgt)
    return data


def _make_cycle_with_exit_gateway() -> BpmnGraphData:
    """start → A → B → GW → {A (retry), end}."""
    data = BpmnGraphData()
    data.nodes["start"] = BpmnNodeDef(
        node_id="start", node_type=BpmnNodeType.START_EVENT
    )
    data.nodes["a"] = BpmnNodeDef(node_id="a", node_type=BpmnNodeType.TASK)
    data.nodes["b"] = BpmnNodeDef(node_id="b", node_type=BpmnNodeType.TASK)
    data.nodes["gw"] = BpmnNodeDef(
        node_id="gw", node_type=BpmnNodeType.EXCLUSIVE_GATEWAY
    )
    data.nodes["end"] = BpmnNodeDef(
        node_id="end", node_type=BpmnNodeType.END_EVENT
    )
    for eid, src, tgt in [
        ("e0", "start", "a"),
        ("e1", "a", "b"),
        ("e2", "b", "gw"),
        ("e3", "gw", "a"),    # retry loop
        ("e4", "gw", "end"),  # exit
    ]:
        data.edges[eid] = BpmnEdgeDef(edge_id=eid, source=src, target=tgt)
    return data


def test_find_loops_finds_cycle() -> None:
    data = _make_unbounded_cycle()
    g = JourneyGraph(data, TripleSet(triples={}))
    cycles = g.all_cycles()
    assert any(set(c) == {"a", "b", "c"} for c in cycles)


def test_unbounded_loop_flagged() -> None:
    data = _make_unbounded_cycle()
    g = JourneyGraph(data, TripleSet(triples={}))
    detections = g.find_unbounded_loops()
    assert len(detections) == 1
    assert detections[0].signal_type == "unbounded_loop"
    assert set(detections[0].detector_context["cycle_nodes"]) == {"a", "b", "c"}


def test_cycle_with_exit_gateway_not_flagged() -> None:
    data = _make_cycle_with_exit_gateway()
    g = JourneyGraph(data, TripleSet(triples={}))
    # There is a cycle a → b → gw → a, and gw has an edge leaving it.
    cycles = g.all_cycles()
    cycle_nodes = {n for c in cycles for n in c}
    assert {"a", "b", "gw"}.issubset(cycle_nodes)
    # But it should not be reported as unbounded.
    detections = g.find_unbounded_loops()
    assert detections == []


def test_analyze_termination_direct() -> None:
    data = _make_cycle_with_exit_gateway()
    g = JourneyGraph(data, TripleSet(triples={}))
    nxg = g.networkx
    cycles = find_loops(nxg)
    analyses = [analyze_loop_termination(nxg, c) for c in cycles]
    assert any(a.has_exit_gateway for a in analyses)
    # At least the cycle containing 'gw' should have exit_node == 'gw'
    matching = [a for a in analyses if a.has_exit_gateway]
    assert all(a.exit_node == "gw" for a in matching)
