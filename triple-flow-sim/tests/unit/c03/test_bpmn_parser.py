"""Unit tests for the BPMN parser.

Spec reference: files/03-journey-graph.md §B1
"""
from __future__ import annotations

from pathlib import Path

import pytest

from triple_flow_sim.components.c03_graph.bpmn_parser import parse_bpmn
from triple_flow_sim.contracts import BpmnNodeType


# ---------------------------------------------------------------------------
# Fixture location — tolerate the example tree living inside the project or
# at its sibling path (C:/.../BMAD/examples/...).
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
def bpmn_data(bpmn_path):
    return parse_bpmn(bpmn_path)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
def test_parse_income_verification(bpmn_data):
    # Reasonably sized BPMN (≥10 nodes).
    assert len(bpmn_data.nodes) >= 10

    node_types = {n.node_type for n in bpmn_data.nodes.values()}
    assert BpmnNodeType.START_EVENT in node_types
    assert BpmnNodeType.END_EVENT in node_types
    assert BpmnNodeType.EXCLUSIVE_GATEWAY in node_types

    # At least one sequence flow must carry a condition.
    assert any(e.condition for e in bpmn_data.edges.values())


def test_parse_condition_stripping(bpmn_data):
    # None of the parsed conditions should still contain a ${...} wrapper.
    for edge in bpmn_data.edges.values():
        if edge.condition is None:
            continue
        assert not edge.condition.startswith("${")
        assert "${" not in edge.condition
        assert not edge.condition.endswith("}")


def test_source_hash_deterministic(bpmn_path):
    first = parse_bpmn(bpmn_path)
    second = parse_bpmn(bpmn_path)
    assert first.source_hash == second.source_hash
    assert len(first.source_hash) == 64  # SHA-256 hex length


def test_all_edges_reference_known_nodes(bpmn_data):
    node_ids = set(bpmn_data.nodes)
    for edge in bpmn_data.edges.values():
        assert edge.source in node_ids
        assert edge.target in node_ids


def test_node_incoming_outgoing_populated(bpmn_data):
    # Every non-start, non-end node should have at least one incoming edge.
    for node in bpmn_data.nodes.values():
        if node.node_type == BpmnNodeType.START_EVENT:
            continue
        if node.node_type == BpmnNodeType.END_EVENT:
            # End events must have incoming.
            assert node.incoming, f"End event {node.node_id} missing incoming"
            continue
        assert node.incoming, f"{node.node_id} should have incoming"
        assert node.outgoing, f"{node.node_id} should have outgoing"
