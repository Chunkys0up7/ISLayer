"""Invariant I8 — tasks and gateways have non-empty psm.enriched_content.

Spec: files/triple-schema.md §I8
"""
from __future__ import annotations

from triple_flow_sim.contracts import (
    BpmnNodeType,
    Evidence,
    Generator,
    RawDetection,
    TripleSet,
)


_CONTENT_REQUIRED_TYPES = {
    BpmnNodeType.TASK,
    BpmnNodeType.EXCLUSIVE_GATEWAY,
    BpmnNodeType.PARALLEL_GATEWAY,
}


def check(triple_set: TripleSet, graph=None) -> list[RawDetection]:
    detections: list[RawDetection] = []
    for triple in triple_set.triples.values():
        if triple.bpmn_node_type not in _CONTENT_REQUIRED_TYPES:
            continue
        if triple.psm is None:
            continue  # I2 handles missing PSM
        content = triple.psm.enriched_content or []
        if not content:
            detections.append(RawDetection(
                signal_type="empty_content",
                generator=Generator.INVENTORY,
                primary_triple_id=triple.triple_id or "<unnamed>",
                bpmn_node_id=triple.bpmn_node_id or None,
                detector_context={
                    "bpmn_node_type": triple.bpmn_node_type.value,
                },
                evidence=Evidence(
                    observed=[],
                    expected="at least one content chunk",
                ),
            ))
    return detections
