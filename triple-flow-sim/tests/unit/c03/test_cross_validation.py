"""Tests for BPMN ↔ derived-topology cross-validation (§B5)."""
from __future__ import annotations

from triple_flow_sim.components.c03_graph import JourneyGraph
from triple_flow_sim.components.c03_graph.bpmn_parser import (
    BpmnEdgeDef,
    BpmnGraphData,
    BpmnNodeDef,
)
from triple_flow_sim.contracts import (
    AssertionPredicate,
    BpmnNodeType,
    ContextAssertion,
    PIMLayer,
    Triple,
    TripleSet,
)


def _bpmn_linear(triple_node_pairs: list[tuple[str, str]]) -> BpmnGraphData:
    """Build a linear BPMN where each given (triple_id, node_id) is a bound task.

    Inserts start/end events at the ends.
    """
    data = BpmnGraphData()
    data.nodes["start"] = BpmnNodeDef(
        node_id="start", node_type=BpmnNodeType.START_EVENT
    )
    data.nodes["end"] = BpmnNodeDef(
        node_id="end", node_type=BpmnNodeType.END_EVENT
    )
    for _, nid in triple_node_pairs:
        data.nodes[nid] = BpmnNodeDef(node_id=nid, node_type=BpmnNodeType.TASK)

    sequence = ["start"] + [nid for _, nid in triple_node_pairs] + ["end"]
    for i in range(len(sequence) - 1):
        eid = f"e{i}"
        data.edges[eid] = BpmnEdgeDef(
            edge_id=eid, source=sequence[i], target=sequence[i + 1]
        )
    return data


def _triple_with_precond(
    tid: str, bpmn_node_id: str, source_triple: str | None, path: str = "x"
) -> Triple:
    pre = None
    if source_triple is not None:
        pre = [
            ContextAssertion(
                path=path,
                predicate=AssertionPredicate.EXISTS,
                source_triple=source_triple,
            )
        ]
    return Triple(
        triple_id=tid,
        bpmn_node_id=bpmn_node_id,
        pim=PIMLayer(preconditions=pre),
    )


def test_bpmn_agrees_with_derived_no_detections() -> None:
    t1 = _triple_with_precond("T1", "n1", source_triple=None)
    t2 = _triple_with_precond("T2", "n2", source_triple="T1")
    bpmn = _bpmn_linear([("T1", "n1"), ("T2", "n2")])
    triple_set = TripleSet(triples={t.triple_id: t for t in [t1, t2]})
    g = JourneyGraph(bpmn, triple_set)
    detections = g.cross_validate_against_derived()
    # Agreement case: no cross-validation detections.
    assert detections == []


def test_derived_but_not_in_bpmn_flagged() -> None:
    # Consumer declares source_triple T1, but BPMN routes T2 before T1.
    t1 = _triple_with_precond("T1", "n1", source_triple=None)
    t2 = _triple_with_precond("T2", "n2", source_triple="T1")
    bpmn = _bpmn_linear([("T2", "n2"), ("T1", "n1")])  # reversed!
    triple_set = TripleSet(triples={t.triple_id: t for t in [t1, t2]})
    g = JourneyGraph(bpmn, triple_set)
    detections = g.cross_validate_against_derived()
    implicit = [d for d in detections if d.signal_type == "handoff_implicit_setup"]
    assert implicit, "Expected at least one handoff_implicit_setup detection"
    assert any(
        d.detector_context.get("direction") == "derived_not_in_bpmn"
        for d in implicit
    )


def test_bpmn_but_not_in_derived_flagged() -> None:
    # BPMN routes T1 → T2 but T2 does not name T1 as a source_triple.
    t1 = _triple_with_precond("T1", "n1", source_triple=None)
    t2 = _triple_with_precond("T2", "n2", source_triple=None)
    bpmn = _bpmn_linear([("T1", "n1"), ("T2", "n2")])
    triple_set = TripleSet(triples={t.triple_id: t for t in [t1, t2]})
    g = JourneyGraph(bpmn, triple_set)
    detections = g.cross_validate_against_derived()
    implicit = [d for d in detections if d.signal_type == "handoff_implicit_setup"]
    assert implicit
    assert any(
        d.detector_context.get("direction") == "bpmn_not_in_derived"
        for d in implicit
    )


def test_no_self_bpmn_edges_reported() -> None:
    """A gateway/event on a single-node indirect expansion must not create
    a self-loop cross-validation finding."""
    t1 = _triple_with_precond("T1", "n1", source_triple=None)
    # Only one bound triple — descent will not create a second endpoint.
    bpmn = _bpmn_linear([("T1", "n1")])
    triple_set = TripleSet(triples={t1.triple_id: t1})
    g = JourneyGraph(bpmn, triple_set)
    detections = g.cross_validate_against_derived()
    for d in detections:
        assert d.detector_context.get("producer") != d.detector_context.get(
            "consumer"
        )
