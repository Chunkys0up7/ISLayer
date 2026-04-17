"""Loop detection for journey graphs.

Spec reference: files/03-journey-graph.md §B6 (structural checks — loop
sub-section).

A loop is a simple cycle in the BPMN graph. Loops that contain an exclusive
gateway with at least one edge leaving the cycle can terminate; loops that do
not are flagged as ``is_potentially_unbounded``.

Phase 2 scope: cycle enumeration + termination heuristic. We deliberately do
NOT do predicate-level bound analysis here — that comes in Phase 3 with
grounded execution.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

import networkx as nx

from triple_flow_sim.contracts import (
    BpmnNodeType,
    Evidence,
    Generator,
    RawDetection,
    TripleSet,
)


@dataclass
class LoopAnalysis:
    """Result of analysing a single cycle in the BPMN graph."""

    cycle_nodes: list[str] = field(default_factory=list)
    has_exit_gateway: bool = False
    exit_node: Optional[str] = None
    is_potentially_unbounded: bool = False


def find_loops(graph: nx.DiGraph) -> list[list[str]]:
    """Return every simple cycle in ``graph`` as an ordered list of node IDs.

    Uses :func:`networkx.simple_cycles`. Self-loops (a single-node cycle) are
    returned as a one-element list. The order of cycles is stable across
    runs for a given graph because ``simple_cycles`` walks the adjacency lists
    in insertion order.
    """
    return [list(c) for c in nx.simple_cycles(graph)]


def analyze_loop_termination(
    graph: nx.DiGraph,
    loop_nodes: list[str],
    triple_set: Optional[TripleSet] = None,  # reserved for future predicate hints
) -> LoopAnalysis:
    """Decide whether the cycle has an exit gateway and is likely bounded.

    A cycle terminates when at least one node on the cycle is an exclusive (or
    inclusive/event-based) gateway whose successor set contains a node NOT on
    the cycle. This is a conservative structural heuristic — a loop without
    such a gateway is flagged as ``is_potentially_unbounded``.
    """
    cycle = list(loop_nodes)
    analysis = LoopAnalysis(cycle_nodes=cycle)
    cycle_set = set(cycle)

    for node_id in cycle:
        node_data = graph.nodes.get(node_id, {})
        nt = node_data.get("node_type")
        # A parallel gateway cannot act as an exit branch (all outgoing edges
        # fire together). Only exclusive-style gateways make a loop bounded.
        if nt != BpmnNodeType.EXCLUSIVE_GATEWAY:
            continue
        for succ in graph.successors(node_id):
            if succ not in cycle_set:
                analysis.has_exit_gateway = True
                analysis.exit_node = node_id
                break
        if analysis.has_exit_gateway:
            break

    analysis.is_potentially_unbounded = not analysis.has_exit_gateway
    return analysis


def detect_unbounded_loops(
    graph: nx.DiGraph,
    triple_set: Optional[TripleSet] = None,
) -> list[RawDetection]:
    """Return one detection per unbounded loop found in ``graph``.

    Each detection carries the cycle nodes in ``detector_context['cycle_nodes']``
    so downstream tooling can render the cycle path.
    """
    detections: list[RawDetection] = []
    for cycle in find_loops(graph):
        analysis = analyze_loop_termination(graph, cycle, triple_set)
        if not analysis.is_potentially_unbounded:
            continue
        # Pick the first bound triple on the cycle for attribution, else empty.
        primary_triple_id = ""
        for node_id in cycle:
            node_data = graph.nodes.get(node_id, {})
            triple = node_data.get("triple")
            if triple is not None:
                primary_triple_id = triple.triple_id
                break
        detections.append(
            RawDetection(
                signal_type="unbounded_loop",
                generator=Generator.INVENTORY,
                primary_triple_id=primary_triple_id or None,
                bpmn_node_id=cycle[0],
                detector_context={
                    "cycle_nodes": cycle,
                    "has_exit_gateway": analysis.has_exit_gateway,
                },
                evidence=Evidence(
                    observed=(
                        f"Cycle {cycle} has no exclusive gateway with an edge "
                        f"leaving the cycle; cannot prove termination."
                    )
                ),
            )
        )
    return detections
