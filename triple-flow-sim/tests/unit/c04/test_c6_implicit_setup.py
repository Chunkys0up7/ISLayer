"""C6 — implicit setup."""
from __future__ import annotations

from triple_flow_sim.components.c04_static_handoff import pair_checks
from triple_flow_sim.contracts import AssertionPredicate, ContextAssertion

from .conftest import make_triple


def test_implicit_setup_when_psm_references_unwritten_path():
    producer = make_triple(
        "prod", "Task_A",
    )
    consumer = make_triple(
        "cons", "Task_B",
        preconditions=[
            ContextAssertion(
                path="z",
                predicate=AssertionPredicate.EXISTS,
                type="any",
            )
        ],
        psm_text="Please use z to finalize the decision.",
    )
    detections = pair_checks.c6_implicit_setup(
        producer, consumer, "E1", upstream_writes={}
    )
    signal_types = [d.signal_type for d in detections]
    assert "handoff_implicit_setup" in signal_types
    d = next(d for d in detections if d.signal_type == "handoff_implicit_setup")
    assert d.detector_context["path"] == "z"
    assert d.detector_context["confidence_hint"] == "medium"


def test_no_implicit_setup_when_no_psm_reference():
    producer = make_triple("prod", "Task_A")
    consumer = make_triple(
        "cons", "Task_B",
        preconditions=[
            ContextAssertion(
                path="zzz",
                predicate=AssertionPredicate.EXISTS,
                type="any",
            )
        ],
        psm_text="Nothing relevant here.",
    )
    detections = pair_checks.c6_implicit_setup(
        producer, consumer, "E1", upstream_writes={}
    )
    assert detections == []
