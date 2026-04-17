"""Tests for derived-topology construction (files/03-journey-graph.md §B4)."""
from __future__ import annotations

from triple_flow_sim.components.c03_graph.derived_topology import (
    build_derived_topology,
    derive_detections,
)
from triple_flow_sim.contracts import (
    AssertionPredicate,
    ContextAssertion,
    PIMLayer,
    Triple,
    TripleSet,
)


def _triple(tid: str, preconditions: list[ContextAssertion] | None = None) -> Triple:
    return Triple(
        triple_id=tid,
        pim=PIMLayer(preconditions=preconditions) if preconditions is not None else None,
    )


def _ts(*triples: Triple) -> TripleSet:
    return TripleSet(triples={t.triple_id: t for t in triples})


def test_chain_edges() -> None:
    t1 = _triple("T1")
    t2 = _triple(
        "T2",
        preconditions=[
            ContextAssertion(
                path="borrower.income",
                predicate=AssertionPredicate.EXISTS,
                source_triple="T1",
            )
        ],
    )
    t3 = _triple(
        "T3",
        preconditions=[
            ContextAssertion(
                path="borrower.dti",
                predicate=AssertionPredicate.EXISTS,
                source_triple="T2",
            )
        ],
    )
    g = build_derived_topology(_ts(t1, t2, t3))
    assert set(g.edges()) == {("T1", "T2"), ("T2", "T3")}


def test_edge_records_source_refs() -> None:
    t2 = _triple(
        "T2",
        preconditions=[
            ContextAssertion(
                path="borrower.income", source_triple="T1",
            ),
            ContextAssertion(
                path="borrower.employment.status", source_triple="T1",
            ),
        ],
    )
    g = build_derived_topology(_ts(_triple("T1"), t2))
    refs = g.edges["T1", "T2"]["source_triple_refs"]
    assert "borrower.income" in refs
    assert "borrower.employment.status" in refs
    assert len(refs) == 2


def test_missing_producer_detection() -> None:
    t2 = _triple(
        "T2",
        preconditions=[
            ContextAssertion(
                path="x", source_triple="NOT_A_REAL_TRIPLE",
            )
        ],
    )
    detections = derive_detections(_ts(t2))
    signals = [d.signal_type for d in detections]
    assert "derived_producer_missing" in signals


def test_self_reference_detection() -> None:
    t = _triple(
        "T1",
        preconditions=[
            ContextAssertion(path="x", source_triple="T1"),
        ],
    )
    detections = derive_detections(_ts(t))
    signals = [d.signal_type for d in detections]
    assert "derived_self_reference" in signals


def test_no_preconditions_is_silent() -> None:
    # PIMLayer present but preconditions explicitly absent — produces no edges.
    t1 = _triple("T1", preconditions=None)
    g = build_derived_topology(_ts(t1))
    assert list(g.edges()) == []
    assert derive_detections(_ts(t1)) == []
