"""Invariant I1 — Identity completeness. Spec: files/triple-schema.md §I1"""
from __future__ import annotations

from triple_flow_sim.contracts import (
    Evidence,
    Generator,
    RawDetection,
    TripleSet,
)


def check(triple_set: TripleSet, graph=None) -> list[RawDetection]:
    """Returns detections for each triple missing any of triple_id/version/bpmn_node_id/bpmn_node_type.

    Note: Triples that already failed I1 are typically excluded from TripleSet by the loader.
    This check still runs for triples that partially loaded (e.g. empty bpmn_node_id strings).
    """
    detections: list[RawDetection] = []
    for triple in triple_set.triples.values():
        missing = []
        if not triple.triple_id:
            missing.append("triple_id")
        if not triple.version or triple.version == "0":
            missing.append("version")
        if not triple.bpmn_node_id:
            missing.append("bpmn_node_id")
        if missing:
            detections.append(RawDetection(
                signal_type="missing_identity_field",
                generator=Generator.INVENTORY,
                primary_triple_id=triple.triple_id or "<unnamed>",
                bpmn_node_id=triple.bpmn_node_id or None,
                detector_context={
                    "missing_fields": missing,
                    "source_path": triple.source_path or "",
                },
                evidence=Evidence(observed=missing, expected="all identity fields populated"),
            ))
    return detections
