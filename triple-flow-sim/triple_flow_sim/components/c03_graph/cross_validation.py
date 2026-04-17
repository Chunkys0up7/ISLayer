"""Cross-validate BPMN routing vs. triple-derived topology.

Spec reference: files/03-journey-graph.md §B5.

For every pair (u, v) either edge set may imply an inter-triple handoff:
  - BPMN says there is a sequence-flow edge from a task bound to producer to
    a task bound to consumer.
  - Derived says consumer's precondition references producer via
    ``source_triple``.

Disagreements surface two high-value signals:
  - BPMN routes the handoff but no contract references it
    → ``handoff_implicit_setup`` (MEDIUM confidence — the simulator suspects
    a silent handoff).
  - Consumer contract names a producer that BPMN does not route through
    → ``handoff_implicit_setup`` (HIGH — declared dependency has no runtime
    path) AND mark ``detector_context['missing_in_bpmn'] = True`` so the
    classifier can distinguish the two directions.

We do not try to repair BPMN here.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

import networkx as nx

from triple_flow_sim.contracts import (
    BpmnNodeType,
    Evidence,
    Generator,
    RawDetection,
)

if TYPE_CHECKING:  # pragma: no cover - typing only
    from triple_flow_sim.components.c03_graph.graph import JourneyGraph


def _bpmn_triple_edges(journey_graph: "JourneyGraph") -> set[tuple[str, str]]:
    """Return (producer_triple_id, consumer_triple_id) for every BPMN edge
    whose source and target are bound to triples.

    Gateway / start / end nodes are skipped; only triple→triple handoffs count
    for B5. Where a gateway sits between two tasks, the edge is expanded by
    taking the gateway's downstream successors until a bound task is reached.
    """
    nxg = journey_graph.networkx
    edges: set[tuple[str, str]] = set()

    for u, v in nxg.edges():
        producer = nxg.nodes[u].get("triple")
        if producer is None:
            continue
        # Direct: both ends bound.
        target_triple = nxg.nodes[v].get("triple")
        if target_triple is not None:
            edges.add((producer.triple_id, target_triple.triple_id))
            continue
        # Indirect: descend through gateways / events until a bound node.
        frontier = [v]
        seen: set[str] = set()
        while frontier:
            node_id = frontier.pop()
            if node_id in seen:
                continue
            seen.add(node_id)
            data = nxg.nodes.get(node_id, {})
            nt = data.get("node_type")
            triple = data.get("triple")
            if triple is not None:
                edges.add((producer.triple_id, triple.triple_id))
                continue
            if nt == BpmnNodeType.END_EVENT:
                continue
            frontier.extend(nxg.successors(node_id))
    return edges


def cross_validate(
    journey_graph: "JourneyGraph",
    derived_graph: nx.DiGraph,
) -> list[RawDetection]:
    """Compare BPMN routing to derived topology and emit RawDetections."""
    detections: list[RawDetection] = []
    bpmn_edges = _bpmn_triple_edges(journey_graph)
    derived_edges: set[tuple[str, str]] = {
        (u, v) for u, v in derived_graph.edges()
    }

    # (1) Derived but not in BPMN: declared dependency with no runtime route.
    for producer, consumer in derived_edges - bpmn_edges:
        detections.append(
            RawDetection(
                signal_type="handoff_implicit_setup",
                generator=Generator.STATIC_HANDOFF,
                primary_triple_id=consumer,
                related_triple_ids=[producer],
                detector_context={
                    "direction": "derived_not_in_bpmn",
                    "missing_in_bpmn": True,
                    "producer": producer,
                    "consumer": consumer,
                },
                evidence=Evidence(
                    observed=(
                        f"Consumer '{consumer}' names '{producer}' as "
                        f"source_triple, but BPMN has no path between them."
                    )
                ),
            )
        )

    # (2) BPMN but not derived: routing exists, no contract references it.
    for producer, consumer in bpmn_edges - derived_edges:
        # Suppress self-loops that can arise from indirect gateway descent.
        if producer == consumer:
            continue
        detections.append(
            RawDetection(
                signal_type="handoff_implicit_setup",
                generator=Generator.STATIC_HANDOFF,
                primary_triple_id=consumer,
                related_triple_ids=[producer],
                detector_context={
                    "direction": "bpmn_not_in_derived",
                    "missing_in_derived": True,
                    "producer": producer,
                    "consumer": consumer,
                },
                evidence=Evidence(
                    observed=(
                        f"BPMN routes '{producer}' → '{consumer}' but "
                        f"'{consumer}' has no precondition referencing "
                        f"'{producer}'."
                    )
                ),
            )
        )

    return detections
