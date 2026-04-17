"""Invariant I6 — every opened obligation is eventually closed or exits the journey.

Spec: files/triple-schema.md §I6
"""
from __future__ import annotations

from triple_flow_sim.contracts import (
    Evidence,
    Generator,
    RawDetection,
    TripleSet,
)


def check(triple_set: TripleSet, graph=None) -> list[RawDetection]:
    # First pass: gather the set of all closed obligation_ids across triples.
    closed_ids: set[str] = set()
    for triple in triple_set.triples.values():
        if triple.pim is None:
            continue
        closed = triple.pim.obligations_closed or []
        for oid in closed:
            if oid:
                closed_ids.add(oid)

    detections: list[RawDetection] = []

    for triple in triple_set.triples.values():
        if triple.pim is None:
            continue
        opened = triple.pim.obligations_opened or []
        for obligation in opened:
            oid = getattr(obligation, "obligation_id", None)
            if not oid:
                continue
            exits_journey = bool(getattr(obligation, "exits_journey", False))
            if exits_journey:
                continue
            if oid in closed_ids:
                continue
            description = getattr(obligation, "description", "") or ""
            detections.append(RawDetection(
                signal_type="orphan_obligation",
                generator=Generator.INVENTORY,
                primary_triple_id=triple.triple_id or "<unnamed>",
                bpmn_node_id=triple.bpmn_node_id or None,
                detector_context={
                    "obligation_id": oid,
                    "obligation_description": description,
                },
                evidence=Evidence(
                    observed=f"opened={oid}",
                    expected="closed somewhere or exits_journey=true",
                ),
            ))
    return detections
