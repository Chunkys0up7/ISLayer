"""Derived topology construction.

Spec reference: files/03-journey-graph.md §B4.

The derived topology expresses the graph **implied by triple contracts** — an
edge from producer to consumer exists whenever some precondition on the
consumer names the producer via ``ContextAssertion.source_triple``.

This is cross-checked against the BPMN routing topology in §B5
(see ``cross_validation.py``). Disagreements between BPMN and derived edges
are the most valuable handoff findings.
"""
from __future__ import annotations

from typing import Optional

import networkx as nx

from triple_flow_sim.contracts import (
    Evidence,
    Generator,
    RawDetection,
    TripleSet,
)


def build_derived_topology(triple_set: TripleSet) -> nx.DiGraph:
    """Build an edge ``producer → consumer`` for every referenced source_triple.

    Nodes are ``triple_id`` strings. Each edge carries:
      - ``source_triple_refs``: list of consumer precondition paths that
        triggered the edge.
    """
    g: nx.DiGraph = nx.DiGraph()
    # First pass: add every known triple as a node so orphan detection is
    # meaningful (a triple no one references is still in the graph).
    for triple in triple_set:
        g.add_node(triple.triple_id)

    # Second pass: add edges from each consumer's source_triple refs.
    for consumer in triple_set:
        pim = consumer.pim
        if pim is None or pim.preconditions is None:
            continue
        for pc in pim.preconditions:
            producer_id = pc.source_triple
            if not producer_id:
                continue
            if producer_id == consumer.triple_id:
                # Self-referential precondition — surface separately.
                continue
            if g.has_edge(producer_id, consumer.triple_id):
                refs = g.edges[producer_id, consumer.triple_id].get(
                    "source_triple_refs", []
                )
                if pc.path not in refs:
                    refs.append(pc.path)
                g.edges[producer_id, consumer.triple_id][
                    "source_triple_refs"
                ] = refs
            else:
                # Ensure node exists even when producer is missing from the
                # set — that's its own finding below.
                if producer_id not in g:
                    g.add_node(producer_id, missing_producer=True)
                g.add_edge(
                    producer_id,
                    consumer.triple_id,
                    source_triple_refs=[pc.path],
                )
    return g


def derive_detections(triple_set: TripleSet) -> list[RawDetection]:
    """Emit detections observable from the derived topology alone.

    - ``derived_producer_missing``: consumer references a ``source_triple`` that
      is not present in the triple set.
    - ``derived_self_reference``: consumer's precondition names itself as the
      source_triple.
    - ``derived_orphan_triple``: a triple neither produces nor consumes any
      handoff (LOW confidence — common for terminal tasks).
    """
    detections: list[RawDetection] = []
    known_ids: set[str] = {t.triple_id for t in triple_set}

    for consumer in triple_set:
        pim = consumer.pim
        if pim is None or pim.preconditions is None:
            continue
        for pc in pim.preconditions:
            if not pc.source_triple:
                continue
            if pc.source_triple == consumer.triple_id:
                detections.append(
                    RawDetection(
                        signal_type="derived_self_reference",
                        generator=Generator.INVENTORY,
                        primary_triple_id=consumer.triple_id,
                        detector_context={"path": pc.path},
                        evidence=Evidence(
                            observed=(
                                f"Triple {consumer.triple_id} declares its own "
                                f"output at {pc.path} as a precondition."
                            )
                        ),
                    )
                )
            elif pc.source_triple not in known_ids:
                detections.append(
                    RawDetection(
                        signal_type="derived_producer_missing",
                        generator=Generator.INVENTORY,
                        primary_triple_id=consumer.triple_id,
                        related_triple_ids=[pc.source_triple],
                        detector_context={
                            "path": pc.path,
                            "missing_source_triple": pc.source_triple,
                        },
                        evidence=Evidence(
                            observed=(
                                f"Precondition source_triple "
                                f"'{pc.source_triple}' is not present in the "
                                f"triple set."
                            )
                        ),
                    )
                )

    return detections


def as_edge_set(g: nx.DiGraph) -> set[tuple[str, str]]:
    """Return the edge set of ``g`` as a plain set of (u, v) tuples."""
    return {(u, v) for u, v in g.edges()}
