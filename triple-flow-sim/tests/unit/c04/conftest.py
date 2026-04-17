"""Shared fixtures for c04 unit tests.

Build tiny BPMN fixtures without hitting disk, bind user-supplied triples,
and construct a JourneyGraph on demand.
"""
from __future__ import annotations

from typing import Optional

import pytest

from triple_flow_sim.components.c03_graph import JourneyGraph
from triple_flow_sim.components.c03_graph.bpmn_parser import (
    BpmnEdgeDef,
    BpmnGraphData,
    BpmnNodeDef,
)
from triple_flow_sim.contracts import (
    AssertionPredicate,
    BpmnNodeType,
    BranchPredicate,
    CIMLayer,
    ContentChunk,
    ContextAssertion,
    MustCloseBy,
    ObligationSpec,
    PIMLayer,
    PSMLayer,
    StateFieldRef,
    Triple,
    TripleSet,
)


def make_triple(
    triple_id: str,
    bpmn_node_id: str,
    *,
    node_type: BpmnNodeType = BpmnNodeType.TASK,
    preconditions: Optional[list[ContextAssertion]] = None,
    postconditions: Optional[list[ContextAssertion]] = None,
    state_reads: Optional[list[StateFieldRef]] = None,
    state_writes: Optional[list[StateFieldRef]] = None,
    obligations_opened: Optional[list[ObligationSpec]] = None,
    obligations_closed: Optional[list[str]] = None,
    decision_predicates: Optional[list[BranchPredicate]] = None,
    psm_text: Optional[str] = None,
) -> Triple:
    psm = PSMLayer(
        enriched_content=(
            [ContentChunk(chunk_id="c1", text=psm_text)] if psm_text else []
        ),
        prompt_scaffold=psm_text,
    )
    return Triple(
        triple_id=triple_id,
        version="1",
        bpmn_node_id=bpmn_node_id,
        bpmn_node_type=node_type,
        cim=CIMLayer(intent="test intent."),
        pim=PIMLayer(
            preconditions=preconditions or [],
            postconditions=postconditions or [],
            state_reads=state_reads or [],
            state_writes=state_writes or [],
            obligations_opened=obligations_opened or [],
            obligations_closed=obligations_closed or [],
            decision_predicates=decision_predicates,
        ),
        psm=psm,
    )


def build_graph(
    nodes: list[tuple[str, BpmnNodeType]],
    edges: list[tuple[str, str, str]],
    triples: list[Triple],
) -> JourneyGraph:
    data = BpmnGraphData(source_hash="a" * 64)
    for node_id, node_type in nodes:
        data.nodes[node_id] = BpmnNodeDef(
            node_id=node_id, node_type=node_type, name=node_id,
        )
    for edge_id, source, target in edges:
        data.edges[edge_id] = BpmnEdgeDef(
            edge_id=edge_id, source=source, target=target,
        )
    ts = TripleSet(triples={t.triple_id: t for t in triples})
    return JourneyGraph(data, ts)


@pytest.fixture
def assertion_equals():
    def _make(path: str, value, type_="string"):
        return ContextAssertion(
            path=path,
            predicate=AssertionPredicate.EQUALS,
            value=value,
            type=type_,
        )
    return _make


@pytest.fixture
def assertion_exists():
    def _make(path: str, type_="any"):
        return ContextAssertion(
            path=path,
            predicate=AssertionPredicate.EXISTS,
            type=type_,
        )
    return _make


@pytest.fixture
def state_field():
    def _make(path: str, type_="string"):
        return StateFieldRef(path=path, type=type_)
    return _make
