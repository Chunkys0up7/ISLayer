"""Unit tests for inventory invariants I1-I10 and the TripleInventory facade."""
from __future__ import annotations

import pytest

from triple_flow_sim.components.c02_inventory import (
    InventoryReport,
    TripleInventory,
)
from triple_flow_sim.components.c02_inventory.invariants import (
    i01_identity,
    i02_layer,
    i03_intent,
    i04_contract,
    i05_gateway_predicates,
    i06_obligation_closure,
    i07_state_flow,
    i08_content_presence,
    i09_predicate_evaluability,
    i10_regulatory_resolution,
)
from triple_flow_sim.contracts import (
    AssertionPredicate,
    BpmnNodeType,
    BranchPredicate,
    BusinessRule,
    CIMLayer,
    ContentChunk,
    ContextAssertion,
    ObligationSpec,
    PIMLayer,
    PSMLayer,
    RegulatoryRef,
    StateFieldRef,
    Triple,
    TripleSet,
)


def _make_triple(
    triple_id: str = "T-01",
    version: str = "1.0",
    bpmn_node_id: str = "N-01",
    node_type: BpmnNodeType = BpmnNodeType.TASK,
    cim: CIMLayer | None = None,
    pim: PIMLayer | None = None,
    psm: PSMLayer | None = None,
) -> Triple:
    return Triple(
        triple_id=triple_id,
        version=version,
        bpmn_node_id=bpmn_node_id,
        bpmn_node_type=node_type,
        cim=cim if cim is not None else CIMLayer(intent="Do something."),
        pim=pim if pim is not None else PIMLayer(
            preconditions=[], postconditions=[], state_reads=[], state_writes=[],
        ),
        psm=psm if psm is not None else PSMLayer(
            enriched_content=[
                ContentChunk(chunk_id="c1", source_document="x", text="stuff")
            ]
        ),
    )


def _ts(*triples: Triple) -> TripleSet:
    return TripleSet(triples={t.triple_id: t for t in triples})


# ---------------------------------------------------------------- I1 identity
def test_i01_missing_bpmn_node_id():
    t = _make_triple(bpmn_node_id="")
    dets = i01_identity.check(_ts(t))
    assert len(dets) == 1
    assert dets[0].signal_type == "missing_identity_field"
    assert "bpmn_node_id" in dets[0].detector_context["missing_fields"]


# ----------------------------------------------------------------- I2 layers
def test_i02_missing_pim():
    t = _make_triple()
    t.pim = None
    dets = i02_layer.check(_ts(t))
    signal = [d for d in dets if d.detector_context.get("layer_name") == "PIM"]
    assert len(signal) == 1


# ------------------------------------------------------------------ I3 intent
def test_i03_multi_sentence_intent():
    t = _make_triple(cim=CIMLayer(intent="First. Second."))
    dets = i03_intent.check(_ts(t))
    assert len(dets) == 1
    assert dets[0].signal_type == "empty_or_multi_sentence_intent"


def test_i03_empty_intent():
    t = _make_triple(cim=CIMLayer(intent=""))
    dets = i03_intent.check(_ts(t))
    assert len(dets) == 1


# --------------------------------------------------------------- I4 contract
def test_i04_missing_postconditions():
    t = _make_triple(pim=PIMLayer(
        preconditions=[], state_reads=[], state_writes=[], postconditions=None,
    ))
    dets = i04_contract.check(_ts(t))
    assert len(dets) == 1
    assert dets[0].detector_context["field_name"] == "pim.postconditions"


def test_i04_all_none():
    t = _make_triple(pim=PIMLayer(
        preconditions=None,
        postconditions=None,
        state_reads=None,
        state_writes=None,
    ))
    dets = i04_contract.check(_ts(t))
    assert len(dets) == 4
    names = {d.detector_context["field_name"] for d in dets}
    assert names == {
        "pim.preconditions",
        "pim.postconditions",
        "pim.state_reads",
        "pim.state_writes",
    }


# ----------------------------------------------------------- I5 gateway preds
def test_i05_gateway_no_predicates():
    t = _make_triple(
        node_type=BpmnNodeType.EXCLUSIVE_GATEWAY,
        pim=PIMLayer(
            preconditions=[],
            postconditions=[],
            state_reads=[],
            state_writes=[],
            decision_predicates=None,
        ),
    )
    dets = i05_gateway_predicates.check(_ts(t))
    assert len(dets) == 1
    assert dets[0].signal_type == "gateway_missing_predicates"


# -------------------------------------------------------- I6 obligation close
def test_i06_orphan_obligation():
    t = _make_triple(pim=PIMLayer(
        preconditions=[],
        postconditions=[],
        state_reads=[],
        state_writes=[],
        obligations_opened=[
            ObligationSpec(obligation_id="OBL-1", description="do X")
        ],
        obligations_closed=[],
    ))
    dets = i06_obligation_closure.check(_ts(t))
    assert len(dets) == 1
    assert dets[0].detector_context["obligation_id"] == "OBL-1"


# --------------------------------------------------------------- I7 state flow
def test_i07_orphan_read():
    t = _make_triple(pim=PIMLayer(
        preconditions=[],
        postconditions=[],
        state_reads=[StateFieldRef(path="unwritten.path")],
        state_writes=[],
    ))
    dets = i07_state_flow.check(_ts(t))
    gaps = [d for d in dets if d.signal_type == "state_flow_gap"]
    assert any(d.detector_context["path"] == "unwritten.path" for d in gaps)


# --------------------------------------------------------------- I8 content
def test_i08_empty_content():
    t = _make_triple(
        node_type=BpmnNodeType.TASK,
        psm=PSMLayer(enriched_content=[]),
    )
    dets = i08_content_presence.check(_ts(t))
    assert len(dets) == 1
    assert dets[0].signal_type == "empty_content"


# ------------------------------------------------------- I9 predicate parse
def test_i09_unparseable_predicate():
    t = _make_triple(
        node_type=BpmnNodeType.EXCLUSIVE_GATEWAY,
        pim=PIMLayer(
            preconditions=[],
            postconditions=[],
            state_reads=[],
            state_writes=[],
            decision_predicates=[
                BranchPredicate(edge_id="edge-1", predicate_expression="a = b")
            ],
        ),
    )
    dets = i09_predicate_evaluability.check(_ts(t))
    bad = [d for d in dets if d.signal_type == "unparseable_predicate"]
    assert len(bad) == 1
    assert bad[0].bpmn_edge_id == "edge-1"


# --------------------------------------------------------- I10 regulatory ref
def test_i10_unresolved_reg_ref():
    t = _make_triple(
        cim=CIMLayer(
            intent="Do thing.",
            regulatory_refs=[RegulatoryRef(citation="REG-A", rule_text="rule A")],
        ),
        pim=PIMLayer(
            preconditions=[],
            postconditions=[],
            state_reads=[],
            state_writes=[],
            obligations_opened=[
                ObligationSpec(
                    obligation_id="OBL-1",
                    regulatory_ref="REG-B",  # Not in cim.regulatory_refs
                )
            ],
        ),
    )
    dets = i10_regulatory_resolution.check(_ts(t))
    assert len(dets) == 1
    assert dets[0].detector_context["citation"] == "REG-B"


# ---------------------------------------------------------- clean-corpus run
def test_inventory_clean_corpus_zero_critical_findings():
    """The 3 clean triples should produce no detections from I1-I10."""
    t1 = _make_triple(
        triple_id="T01", bpmn_node_id="N1",
        node_type=BpmnNodeType.START_EVENT,
        pim=PIMLayer(
            preconditions=[],
            postconditions=[ContextAssertion(path="a.started", predicate=AssertionPredicate.EXISTS)],
            state_reads=[],
            state_writes=[StateFieldRef(path="a.started")],
        ),
        psm=PSMLayer(enriched_content=[]),
    )
    t2 = _make_triple(
        triple_id="T02", bpmn_node_id="N2",
        node_type=BpmnNodeType.TASK,
        pim=PIMLayer(
            preconditions=[ContextAssertion(path="a.started", predicate=AssertionPredicate.EXISTS)],
            postconditions=[ContextAssertion(path="a.done", predicate=AssertionPredicate.EXISTS)],
            state_reads=[StateFieldRef(path="a.started")],
            state_writes=[StateFieldRef(path="a.done")],
        ),
    )
    t3 = _make_triple(
        triple_id="T03", bpmn_node_id="N3",
        node_type=BpmnNodeType.END_EVENT,
        pim=PIMLayer(
            preconditions=[ContextAssertion(path="a.done", predicate=AssertionPredicate.EXISTS)],
            postconditions=[],
            state_reads=[StateFieldRef(path="a.done")],
            state_writes=[],
        ),
        psm=PSMLayer(enriched_content=[]),
    )
    inv = TripleInventory(_ts(t1, t2, t3))
    report = inv.run()
    # Naming drift may emit between similar paths; but I1-I10 should not fire.
    core_signals = {
        "missing_identity_field", "missing_layer", "empty_or_multi_sentence_intent",
        "missing_contract_field", "gateway_missing_predicates", "orphan_obligation",
        "state_flow_gap", "empty_content", "unparseable_predicate",
        "unresolved_regulatory_ref",
    }
    core_detections = [d for d in report.raw_detections if d.signal_type in core_signals]
    assert core_detections == []
    assert isinstance(report, InventoryReport)
    assert report.total_triples == 3
