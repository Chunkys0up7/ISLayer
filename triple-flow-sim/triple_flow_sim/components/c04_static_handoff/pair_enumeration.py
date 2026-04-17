"""Enumerate (producer, consumer, edge_id) triples from the journey graph.

Spec reference: files/04-static-handoff-checker.md §B1
"""
from __future__ import annotations

from typing import Optional

from triple_flow_sim.contracts import BpmnNodeType


_TASK_LIKE = {
    BpmnNodeType.TASK,
    BpmnNodeType.START_EVENT,
    BpmnNodeType.END_EVENT,
    BpmnNodeType.INTERMEDIATE_EVENT,
}


def enumerate_pairs(graph) -> list[tuple[str, str, Optional[str]]]:
    """Return (producer_node_id, consumer_node_id, edge_id) for every edge
    where both endpoints are task-like nodes with bound triples.

    Skips edges where either endpoint is a gateway — those are handled by
    gateway_checks. Start→first-task and last-task→end are included when
    both endpoints are bound to triples.
    """
    pairs: list[tuple[str, str, Optional[str]]] = []
    nx = graph.networkx
    for u, v in nx.edges():
        u_data = nx.nodes[u]
        v_data = nx.nodes[v]
        if u_data["node_type"] not in _TASK_LIKE:
            continue
        if v_data["node_type"] not in _TASK_LIKE:
            continue
        producer = u_data.get("triple")
        consumer = v_data.get("triple")
        if producer is None or consumer is None:
            continue
        edge_data = nx.get_edge_data(u, v) or {}
        pairs.append((u, v, edge_data.get("edge_id")))
    return pairs
