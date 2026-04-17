"""C4 — obligation propagation."""
from __future__ import annotations

from triple_flow_sim.components.c04_static_handoff import pair_checks
from triple_flow_sim.contracts import ObligationSpec

from .conftest import make_triple


def test_orphan_obligation_when_successor_does_not_close():
    ob = ObligationSpec(
        obligation_id="OB_1",
        description="Notify borrower within 3 business days",
    )
    producer = make_triple(
        "prod", "Task_A",
        obligations_opened=[ob],
    )
    consumer = make_triple(
        "cons", "Task_B",
        obligations_closed=[],
    )
    detections = pair_checks.c4_obligations(
        producer, consumer, "E1", downstream_closes=set()
    )
    assert len(detections) == 1
    d = detections[0]
    assert d.signal_type == "orphan_obligation"
    assert d.detector_context["obligation_id"] == "OB_1"
    assert d.primary_triple_id == "prod"


def test_no_detection_when_successor_closes():
    ob = ObligationSpec(
        obligation_id="OB_1",
        description="Notify borrower within 3 business days",
    )
    producer = make_triple(
        "prod", "Task_A",
        obligations_opened=[ob],
    )
    consumer = make_triple(
        "cons", "Task_B",
        obligations_closed=["OB_1"],
    )
    detections = pair_checks.c4_obligations(
        producer, consumer, "E1", downstream_closes=set()
    )
    assert detections == []
