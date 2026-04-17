"""Unit tests for JourneyGraph construction and traversal.

Spec reference: files/03-journey-graph.md §B6, §B7
"""
from __future__ import annotations

from pathlib import Path

import pytest

from triple_flow_sim.components.c03_graph import JourneyGraph
from triple_flow_sim.components.c03_graph.bpmn_parser import (
    BpmnEdgeDef,
    BpmnGraphData,
    BpmnNodeDef,
    parse_bpmn,
)
from triple_flow_sim.contracts import (
    BpmnNodeType,
    Triple,
    TripleSet,
)


# ---------------------------------------------------------------------------
# Fixture location
# ---------------------------------------------------------------------------
_CANDIDATE_PATHS = [
    Path(__file__).parents[3] / "examples" / "income-verification" / "bpmn" / "income-verification.bpmn",
    Path(__file__).parents[4] / "examples" / "income-verification" / "bpmn" / "income-verification.bpmn",
]


def _resolve_bpmn_path() -> Path:
    for p in _CANDIDATE_PATHS:
        if p.exists():
            return p
    pytest.skip(
        "Income verification BPMN fixture not found. Tried: "
        + ", ".join(str(p) for p in _CANDIDATE_PATHS)
    )


@pytest.fixture(scope="module")
def bpmn_path() -> Path:
    return _resolve_bpmn_path()


@pytest.fixture(scope="module")
def empty_triple_set() -> TripleSet:
    return TripleSet(triples={})


@pytest.fixture(scope="module")
def graph(bpmn_path, empty_triple_set) -> JourneyGraph:
    return JourneyGraph.from_bpmn_file(bpmn_path, empty_triple_set)


# ---------------------------------------------------------------------------
# Tests against the income-verification example
# ---------------------------------------------------------------------------
def test_graph_build(graph):
    assert len(graph.start_events()) >= 1
    assert len(graph.end_events()) >= 1


def test_traversal_successors(graph):
    # Task_ReceiveRequest should flow into Task_ClassifyEmployment in the
    # income-verification example.
    starts = graph.start_events()
    assert starts, "expected at least one start event"
    # Each start event must have at least one successor.
    for s in starts:
        assert graph.successors(s), f"start {s} has no successors"


def test_pairs_to_check(graph):
    pairs = graph.pairs_to_check()
    assert pairs, "pairs_to_check must be non-empty for a real BPMN"
    for u, v in pairs:
        # Every pair must correspond to an actual edge in the underlying graph.
        assert v in graph.successors(u)


def test_is_reachable_start_to_end(graph):
    starts = graph.start_events()
    ends = graph.end_events()
    assert any(
        graph.is_reachable(s, e) for s in starts for e in ends
    ), "no start can reach any end event"


def test_critical_path_heuristic(graph):
    # With no config, at least one node should land on the heuristic path.
    assert graph.critical_path, "expected non-empty heuristic critical path"
    # Starts and ends that connect must be on that path.
    for s in graph.start_events():
        for e in graph.end_events():
            if graph.is_reachable(s, e):
                assert s in graph.critical_path
                assert e in graph.critical_path


def test_critical_path_config_override(bpmn_path, empty_triple_set):
    # When config provides a critical path, it takes precedence verbatim.
    bpmn_data = parse_bpmn(bpmn_path)
    picked = next(iter(bpmn_data.nodes))  # pick any valid node id
    g = JourneyGraph.from_bpmn_file(
        bpmn_path, empty_triple_set, config_critical_path=[picked]
    )
    assert g.critical_path == {picked}
    assert g.is_on_critical_path(picked)


def test_edges_from_carry_condition_and_default(graph):
    # Find at least one gateway and confirm edges_from returns conditions.
    gateways = [
        n for n in graph.networkx.nodes
        if graph.networkx.nodes[n]["node_type"] == BpmnNodeType.EXCLUSIVE_GATEWAY
    ]
    assert gateways, "income-verification should have gateways"
    conditioned = False
    for g_id in gateways:
        for edge in graph.edges_from(g_id):
            if edge["condition"]:
                conditioned = True
                break
    assert conditioned, "at least one gateway outgoing edge should have a condition"


# ---------------------------------------------------------------------------
# Synthetic graph to test structural detections end-to-end
# ---------------------------------------------------------------------------
def _make_synthetic_graph() -> BpmnGraphData:
    """Tiny BPMN: Start -> Task_A -> End; plus an orphan Task_Orphan."""
    data = BpmnGraphData(source_hash="x" * 64)
    data.nodes["Start_1"] = BpmnNodeDef(
        node_id="Start_1", node_type=BpmnNodeType.START_EVENT, name="Start",
    )
    data.nodes["Task_A"] = BpmnNodeDef(
        node_id="Task_A", node_type=BpmnNodeType.TASK, name="A",
    )
    data.nodes["End_1"] = BpmnNodeDef(
        node_id="End_1", node_type=BpmnNodeType.END_EVENT, name="End",
    )
    data.nodes["Task_Orphan"] = BpmnNodeDef(
        node_id="Task_Orphan", node_type=BpmnNodeType.TASK, name="Orphan",
    )
    data.edges["F1"] = BpmnEdgeDef(
        edge_id="F1", source="Start_1", target="Task_A"
    )
    data.edges["F2"] = BpmnEdgeDef(
        edge_id="F2", source="Task_A", target="End_1"
    )
    return data


def test_orphan_detection():
    bpmn = _make_synthetic_graph()
    # Bind a triple to the orphan node.
    triple_orphan = Triple(
        triple_id="triple-orphan",
        bpmn_node_id="Task_Orphan",
        bpmn_node_type=BpmnNodeType.TASK,
    )
    triple_ok = Triple(
        triple_id="triple-ok",
        bpmn_node_id="Task_A",
        bpmn_node_type=BpmnNodeType.TASK,
    )
    ts = TripleSet(
        triples={"triple-orphan": triple_orphan, "triple-ok": triple_ok}
    )
    graph = JourneyGraph(bpmn, ts)

    # Bindings exist for both tasks.
    assert graph.get_triple("Task_Orphan") is triple_orphan
    assert graph.get_triple("Task_A") is triple_ok

    # Detections should include an orphan_triple for Task_Orphan via the
    # unreachable-from-start and dead-end checks.
    detections = graph.detections
    reasons = {
        (d.bpmn_node_id, d.detector_context.get("reason"))
        for d in detections
        if d.signal_type == "orphan_triple"
    }
    assert ("Task_Orphan", "unreachable_from_start") in reasons
    assert ("Task_Orphan", "dead_end") in reasons

    # Task_A is reachable and flows into End_1, so it should NOT produce an
    # unreachable or dead-end detection.
    assert ("Task_A", "unreachable_from_start") not in reasons
    assert ("Task_A", "dead_end") not in reasons


def test_orphan_bpmn_node_detection():
    # Synthetic graph where the node has no bound triple.
    bpmn = _make_synthetic_graph()
    ts = TripleSet(triples={})
    graph = JourneyGraph(bpmn, ts)
    detections = graph.detections
    orphan_node_ids = {
        d.bpmn_node_id
        for d in detections
        if d.signal_type == "orphan_bpmn_node"
    }
    # Task_A and Task_Orphan are unbound (Start/End excluded by design).
    assert "Task_A" in orphan_node_ids
    assert "Task_Orphan" in orphan_node_ids
    assert "Start_1" not in orphan_node_ids
    assert "End_1" not in orphan_node_ids


def test_traversal_helpers_on_synthetic():
    bpmn = _make_synthetic_graph()
    graph = JourneyGraph(bpmn, TripleSet(triples={}))
    assert graph.start_events() == ["Start_1"]
    assert graph.end_events() == ["End_1"]
    assert graph.successors("Start_1") == ["Task_A"]
    assert graph.predecessors("End_1") == ["Task_A"]
    assert graph.is_reachable("Start_1", "End_1")
    assert not graph.is_reachable("Task_Orphan", "End_1")
    paths = graph.all_paths("Start_1", "End_1")
    assert paths == [["Start_1", "Task_A", "End_1"]]
    assert graph.pairs_to_check() == [
        ("Start_1", "Task_A"),
        ("Task_A", "End_1"),
    ]
