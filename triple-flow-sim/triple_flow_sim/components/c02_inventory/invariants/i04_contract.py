"""Invariant I4 — pim contract fields are all declared (may be empty).

Fields that may be None (not declared) on the PIM layer:
  preconditions, postconditions, state_reads, state_writes.

None -> emit missing_contract_field (per field).

Spec: files/triple-schema.md §I4
"""
from __future__ import annotations

from triple_flow_sim.contracts import (
    Evidence,
    Generator,
    RawDetection,
    TripleSet,
)


_REQUIRED_FIELDS = (
    "preconditions",
    "postconditions",
    "state_reads",
    "state_writes",
)


def check(triple_set: TripleSet, graph=None) -> list[RawDetection]:
    detections: list[RawDetection] = []
    for triple in triple_set.triples.values():
        if triple.pim is None:
            continue  # I2 handles this
        for field in _REQUIRED_FIELDS:
            if getattr(triple.pim, field, None) is None:
                field_name = f"pim.{field}"
                detections.append(RawDetection(
                    signal_type="missing_contract_field",
                    generator=Generator.INVENTORY,
                    primary_triple_id=triple.triple_id or "<unnamed>",
                    bpmn_node_id=triple.bpmn_node_id or None,
                    detector_context={"field_name": field_name},
                    evidence=Evidence(
                        observed=None,
                        expected=f"{field_name} declared (may be empty list)",
                    ),
                ))
    return detections
