"""Invariant I5 — gateways declare decision_predicates.

Spec: files/triple-schema.md §I5
"""
from __future__ import annotations

from triple_flow_sim.contracts import (
    BpmnNodeType,
    Evidence,
    Generator,
    RawDetection,
    TripleSet,
)


_GATEWAY_TYPES = {BpmnNodeType.EXCLUSIVE_GATEWAY, BpmnNodeType.PARALLEL_GATEWAY}


def check(triple_set: TripleSet, graph=None) -> list[RawDetection]:
    detections: list[RawDetection] = []
    for triple in triple_set.triples.values():
        if triple.bpmn_node_type not in _GATEWAY_TYPES:
            continue
        preds = None
        if triple.pim is not None:
            preds = triple.pim.decision_predicates
        if not preds:
            detections.append(RawDetection(
                signal_type="gateway_missing_predicates",
                generator=Generator.INVENTORY,
                primary_triple_id=triple.triple_id or "<unnamed>",
                bpmn_node_id=triple.bpmn_node_id or None,
                detector_context={
                    "bpmn_node_type": triple.bpmn_node_type.value,
                },
                evidence=Evidence(
                    observed=preds,
                    expected="at least one decision_predicate for gateway",
                ),
            ))
    return detections
