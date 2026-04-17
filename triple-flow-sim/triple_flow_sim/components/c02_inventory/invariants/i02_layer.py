"""Invariant I2 — Every triple has cim, pim, psm objects (non-None).

Spec: files/triple-schema.md §I2
"""
from __future__ import annotations

from triple_flow_sim.contracts import (
    Evidence,
    Generator,
    RawDetection,
    TripleSet,
)


_LAYERS = (("cim", "CIM"), ("pim", "PIM"), ("psm", "PSM"))


def check(triple_set: TripleSet, graph=None) -> list[RawDetection]:
    detections: list[RawDetection] = []
    for triple in triple_set.triples.values():
        for attr, layer_name in _LAYERS:
            if getattr(triple, attr, None) is None:
                detections.append(RawDetection(
                    signal_type="missing_layer",
                    generator=Generator.INVENTORY,
                    primary_triple_id=triple.triple_id or "<unnamed>",
                    bpmn_node_id=triple.bpmn_node_id or None,
                    detector_context={"layer_name": layer_name},
                    evidence=Evidence(observed=None, expected=f"{layer_name} layer populated"),
                ))
    return detections
