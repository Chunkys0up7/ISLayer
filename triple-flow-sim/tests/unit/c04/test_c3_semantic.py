"""C3 — semantic satisfaction via symbolic evaluator."""
from __future__ import annotations

from triple_flow_sim.components.c04_static_handoff import pair_checks
from triple_flow_sim.evaluator.symbolic import SymbolicEvaluator

from .conftest import make_triple


def test_never_satisfied_equals_emits_format_mismatch(assertion_equals):
    producer = make_triple(
        "prod", "Task_A",
        postconditions=[assertion_equals("decision", "approved")],
    )
    consumer = make_triple(
        "cons", "Task_B",
        preconditions=[assertion_equals("decision", "rejected")],
    )
    sym = SymbolicEvaluator()
    detections = pair_checks.c3_semantic(
        producer, consumer, "E1", symbolic=sym
    )
    signal_types = [d.signal_type for d in detections]
    assert "handoff_format_mismatch" in signal_types
    d = next(d for d in detections if d.signal_type == "handoff_format_mismatch")
    assert d.detector_context["verdict"] == "never_satisfied"


def test_always_satisfied_emits_nothing(assertion_equals):
    producer = make_triple(
        "prod", "Task_A",
        postconditions=[assertion_equals("decision", "approved")],
    )
    consumer = make_triple(
        "cons", "Task_B",
        preconditions=[assertion_equals("decision", "approved")],
    )
    sym = SymbolicEvaluator()
    detections = pair_checks.c3_semantic(
        producer, consumer, "E1", symbolic=sym
    )
    assert detections == []
