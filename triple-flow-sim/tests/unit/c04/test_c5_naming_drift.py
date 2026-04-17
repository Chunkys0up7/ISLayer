"""C5 — naming drift."""
from __future__ import annotations

from triple_flow_sim.components.c04_static_handoff import pair_checks

from .conftest import make_triple


def test_naming_drift_detected_on_dotted_vs_underscore(state_field):
    producer = make_triple(
        "prod", "Task_A",
        state_writes=[state_field("income.amount", "decimal")],
    )
    consumer = make_triple(
        "cons", "Task_B",
        state_reads=[state_field("income_amount", "decimal")],
    )
    detections = pair_checks.c5_naming_drift(producer, consumer, "E1")
    assert len(detections) == 1
    d = detections[0]
    assert d.signal_type == "handoff_naming_drift"
    ctx = d.detector_context
    assert ctx["path_a"] == "income.amount"
    assert ctx["path_b"] == "income_amount"


def test_no_drift_when_paths_identical(state_field):
    producer = make_triple(
        "prod", "Task_A",
        state_writes=[state_field("income.amount", "decimal")],
    )
    consumer = make_triple(
        "cons", "Task_B",
        state_reads=[state_field("income.amount", "decimal")],
    )
    detections = pair_checks.c5_naming_drift(producer, consumer, "E1")
    assert detections == []
