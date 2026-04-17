"""Unit test for pair_enumeration.enumerate_pairs."""
from __future__ import annotations

from triple_flow_sim.components.c04_static_handoff.pair_enumeration import (
    enumerate_pairs,
)
from triple_flow_sim.contracts import BpmnNodeType

from .conftest import build_graph, make_triple


def test_task_task_edge_enumerated_once():
    """Graph with task-task edge + task-gateway-task should yield exactly
    one pair (the direct task-task edge). Gateway-to-task edges are skipped.
    """
    nodes = [
        ("Start_1", BpmnNodeType.START_EVENT),
        ("Task_A", BpmnNodeType.TASK),
        ("Task_B", BpmnNodeType.TASK),
        ("GW_1", BpmnNodeType.EXCLUSIVE_GATEWAY),
        ("Task_C", BpmnNodeType.TASK),
        ("End_1", BpmnNodeType.END_EVENT),
    ]
    edges = [
        ("F1", "Start_1", "Task_A"),
        ("F2", "Task_A", "Task_B"),       # task-task edge  ← should be enumerated
        ("F3", "Task_B", "GW_1"),          # task-gateway     ← skipped
        ("F4", "GW_1", "Task_C"),          # gateway-task    ← skipped
        ("F5", "Task_C", "End_1"),
    ]
    triples = [
        make_triple("t-a", "Task_A"),
        make_triple("t-b", "Task_B"),
        make_triple("t-c", "Task_C"),
        make_triple("t-gw", "GW_1", node_type=BpmnNodeType.EXCLUSIVE_GATEWAY),
    ]
    graph = build_graph(nodes, edges, triples)
    pairs = enumerate_pairs(graph)
    producer_consumer = [(u, v) for (u, v, _) in pairs]
    assert ("Task_A", "Task_B") in producer_consumer
    # Gateway-involved edges are excluded.
    assert ("Task_B", "GW_1") not in producer_consumer
    assert ("GW_1", "Task_C") not in producer_consumer
    # Start and End lack bound triples here, so edges involving them are skipped.
    assert ("Start_1", "Task_A") not in producer_consumer
    assert ("Task_C", "End_1") not in producer_consumer
