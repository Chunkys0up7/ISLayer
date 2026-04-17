"""Bind triples to BPMN nodes.

Spec reference: files/03-journey-graph.md §B2
"""
from __future__ import annotations

from triple_flow_sim.contracts import (
    BpmnNodeType,
    Evidence,
    Generator,
    RawDetection,
    Triple,
    TripleSet,
)
from triple_flow_sim.components.c03_graph.bpmn_parser import BpmnGraphData


def bind(
    triple_set: TripleSet, bpmn_data: BpmnGraphData
) -> tuple[dict[str, Triple], list[RawDetection]]:
    """Build node_id -> Triple bindings and emit orphan detections.

    Returns
    -------
    bindings : dict[str, Triple]
        Keyed by bpmn_node_id. A triple is bound to node X iff its
        ``bpmn_node_id`` equals X and X exists in the BPMN model.
    detections : list[RawDetection]
        - ``signal_type="orphan_bpmn_node"`` for BPMN nodes with no matching
          triple. START_EVENT and END_EVENT nodes are intentionally excluded
          from this check because those are allowed to be unbound.

    ``orphan_triple`` detections (reachability, dead-ends, non-existent
    node references) are emitted by ``graph.py`` instead — see §B6.
    """
    bindings: dict[str, Triple] = {}
    detections: list[RawDetection] = []

    # Collect bindings and note triples referencing non-existent nodes.
    for triple in triple_set:
        node_id = getattr(triple, "bpmn_node_id", "") or ""
        if not node_id:
            continue
        if node_id in bpmn_data.nodes:
            bindings[node_id] = triple
        else:
            # Triple points at a node that doesn't exist in the BPMN.
            detections.append(
                RawDetection(
                    signal_type="orphan_triple",
                    generator=Generator.INVENTORY,
                    primary_triple_id=triple.triple_id,
                    bpmn_node_id=node_id,
                    detector_context={"reason": "bpmn_node_not_found"},
                    evidence=Evidence(
                        observed=(
                            f"Triple {triple.triple_id} references "
                            f"bpmn_node_id={node_id!r} which does not exist"
                        )
                    ),
                )
            )

    # Orphan BPMN nodes (no triple bound), excluding Start/End events.
    for node_id, node in bpmn_data.nodes.items():
        if node_id in bindings:
            continue
        if node.node_type in (BpmnNodeType.START_EVENT, BpmnNodeType.END_EVENT):
            continue
        detections.append(
            RawDetection(
                signal_type="orphan_bpmn_node",
                generator=Generator.INVENTORY,
                primary_triple_id=None,
                bpmn_node_id=node_id,
                detector_context={
                    "node_type": node.node_type.value,
                    "name": node.name,
                },
                evidence=Evidence(
                    observed=(
                        f"BPMN node {node_id} ({node.node_type.value}) "
                        f"has no bound triple"
                    )
                ),
            )
        )

    return bindings, detections
