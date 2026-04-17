"""Invariant I10 — every obligation.regulatory_ref resolves to a cim.regulatory_refs citation.

Spec: files/triple-schema.md §I10
"""
from __future__ import annotations

from triple_flow_sim.contracts import (
    Evidence,
    Generator,
    RawDetection,
    TripleSet,
)


def check(triple_set: TripleSet, graph=None) -> list[RawDetection]:
    detections: list[RawDetection] = []
    for triple in triple_set.triples.values():
        if triple.pim is None:
            continue
        opened = triple.pim.obligations_opened or []
        if not opened:
            continue
        # Known citations for this triple
        citations: set[str] = set()
        if triple.cim is not None:
            for ref in triple.cim.regulatory_refs or []:
                cite = getattr(ref, "citation", None)
                if cite:
                    citations.add(cite)
        for obligation in opened:
            reg_ref = getattr(obligation, "regulatory_ref", None)
            if not reg_ref:
                continue
            if reg_ref in citations:
                continue
            oid = getattr(obligation, "obligation_id", "") or ""
            detections.append(RawDetection(
                signal_type="unresolved_regulatory_ref",
                generator=Generator.INVENTORY,
                primary_triple_id=triple.triple_id or "<unnamed>",
                bpmn_node_id=triple.bpmn_node_id or None,
                detector_context={
                    "obligation_id": oid,
                    "citation": reg_ref,
                },
                evidence=Evidence(
                    observed=reg_ref,
                    expected=f"citation present in cim.regulatory_refs of {triple.triple_id}",
                ),
            ))
    return detections
