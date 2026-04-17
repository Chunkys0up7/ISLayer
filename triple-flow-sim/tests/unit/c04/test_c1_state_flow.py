"""C1 — state flow coverage."""
from __future__ import annotations

from triple_flow_sim.components.c04_static_handoff import pair_checks

from .conftest import make_triple


def test_state_flow_gap_when_paths_differ(state_field):
    producer = make_triple(
        "prod", "Task_A",
        state_writes=[state_field("x", "string")],
    )
    consumer = make_triple(
        "cons", "Task_B",
        state_reads=[state_field("y", "string")],
    )
    detections = pair_checks.c1_state_flow(producer, consumer, "E1")
    signal_types = [d.signal_type for d in detections]
    assert "state_flow_gap" in signal_types
    gap = next(d for d in detections if d.signal_type == "state_flow_gap")
    assert gap.detector_context["path"] == "y"
    assert gap.related_triple_ids == ["prod"]


def test_no_detection_when_paths_match(state_field):
    producer = make_triple(
        "prod", "Task_A",
        state_writes=[state_field("x", "string")],
    )
    consumer = make_triple(
        "cons", "Task_B",
        state_reads=[state_field("x", "string")],
    )
    detections = pair_checks.c1_state_flow(producer, consumer, "E1")
    assert detections == []
