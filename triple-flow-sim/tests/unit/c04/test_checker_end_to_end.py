"""End-to-end smoke for StaticHandoffChecker.check_all()."""
from __future__ import annotations

from triple_flow_sim.components.c04_static_handoff import StaticHandoffChecker
from triple_flow_sim.contracts import BpmnNodeType

from .conftest import build_graph, make_triple


def test_end_to_end_small_fixture_graph(state_field):
    """Tiny Start -> Task_A -> Task_B -> End graph where Task_B reads a path
    Task_A never writes. Expect at least one state_flow_gap in the report.
    """
    nodes = [
        ("Start_1", BpmnNodeType.START_EVENT),
        ("Task_A", BpmnNodeType.TASK),
        ("Task_B", BpmnNodeType.TASK),
        ("End_1", BpmnNodeType.END_EVENT),
    ]
    edges = [
        ("F1", "Start_1", "Task_A"),
        ("F2", "Task_A", "Task_B"),
        ("F3", "Task_B", "End_1"),
    ]
    t_a = make_triple(
        "t-a", "Task_A",
        state_writes=[state_field("x", "string")],
    )
    t_b = make_triple(
        "t-b", "Task_B",
        state_reads=[state_field("y", "string")],
    )
    graph = build_graph(nodes, edges, [t_a, t_b])
    checker = StaticHandoffChecker(graph)
    report = checker.check_all()

    assert report.pairs_checked >= 1
    all_det = report.all_detections()
    signal_types = {d.signal_type for d in all_det}
    assert "state_flow_gap" in signal_types

    # Shape checks
    found_pair = next(
        r for r in report.pair_results
        if r.producer_id == "Task_A" and r.consumer_id == "Task_B"
    )
    assert found_pair.verdict == "fail"
    assert found_pair.edge_id == "F2"
