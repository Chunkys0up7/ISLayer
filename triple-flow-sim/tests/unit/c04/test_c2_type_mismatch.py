"""C2 — type compatibility."""
from __future__ import annotations

from triple_flow_sim.contracts import AssertionPredicate, ContextAssertion

from triple_flow_sim.components.c04_static_handoff import pair_checks

from .conftest import make_triple


def test_type_mismatch_on_same_path(state_field):
    producer = make_triple(
        "prod", "Task_A",
        postconditions=[
            ContextAssertion(
                path="amount",
                predicate=AssertionPredicate.EXISTS,
                type="string",
            )
        ],
        state_writes=[state_field("amount", "string")],
    )
    consumer = make_triple(
        "cons", "Task_B",
        preconditions=[
            ContextAssertion(
                path="amount",
                predicate=AssertionPredicate.EXISTS,
                type="decimal",
            )
        ],
    )
    detections = pair_checks.c2_type_mismatch(producer, consumer, "E1")
    assert len(detections) == 1
    d = detections[0]
    assert d.signal_type == "type_mismatch"
    assert d.detector_context["path"] == "amount"
    assert d.detector_context["expected_type"] == "decimal"
    assert d.detector_context["observed_type"] == "string"
