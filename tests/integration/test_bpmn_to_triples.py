"""Integration tests: BPMN parsing and triple directory structure.

Parametrized over all 3 demo processes via the example_process fixture.
"""

import sys
from pathlib import Path
from collections import deque

import pytest

# Ensure tests/ is importable so we can access conftest constants
_TESTS_DIR = Path(__file__).resolve().parent.parent
if str(_TESTS_DIR) not in sys.path:
    sys.path.insert(0, str(_TESTS_DIR))

from conftest import EXPECTED, EXAMPLES_DIR, discover_triple_dirs  # noqa: E402

# conftest adds cli/ to sys.path
from mda_io.bpmn_xml import parse_bpmn  # noqa: E402


class TestBpmnParsing:
    """Verify BPMN parsing succeeds and produces correct counts."""

    def test_bpmn_parses_without_error(self, example_process):
        """parse_bpmn should succeed on every demo BPMN file."""
        model = parse_bpmn(example_process["bpmn_path"])
        assert model is not None
        assert len(model.nodes) > 0

    def test_node_count_matches(self, example_process):
        """Parsed node count must equal expected total_nodes."""
        model = parse_bpmn(example_process["bpmn_path"])
        expected_count = example_process["expected"]["total_nodes"]
        assert len(model.nodes) == expected_count, (
            f"{example_process['name']}: expected {expected_count} nodes, "
            f"got {len(model.nodes)}"
        )

    def test_edge_count_matches(self, example_process):
        """Parsed edge count must equal expected edges."""
        model = parse_bpmn(example_process["bpmn_path"])
        expected_count = example_process["expected"]["edges"]
        assert len(model.edges) == expected_count, (
            f"{example_process['name']}: expected {expected_count} edges, "
            f"got {len(model.edges)}"
        )

    def test_lane_count_matches(self, example_process):
        """Parsed lane count must equal expected lanes."""
        model = parse_bpmn(example_process["bpmn_path"])
        expected_count = example_process["expected"]["lanes"]
        assert len(model.lanes) == expected_count, (
            f"{example_process['name']}: expected {expected_count} lanes, "
            f"got {len(model.lanes)}"
        )

    def test_all_edges_connect_valid_nodes(self, example_process):
        """Every edge source and target must reference a known node ID."""
        model = parse_bpmn(example_process["bpmn_path"])
        node_ids = {n.id for n in model.nodes}
        for edge in model.edges:
            assert edge.source_id in node_ids, (
                f"Edge {edge.id} has unknown source {edge.source_id}"
            )
            assert edge.target_id in node_ids, (
                f"Edge {edge.id} has unknown target {edge.target_id}"
            )

    def test_graph_connected_from_start(self, example_process):
        """BFS from any startEvent should reach all other nodes (undirected)."""
        model = parse_bpmn(example_process["bpmn_path"])

        # Build undirected adjacency from edges
        adj: dict[str, set[str]] = {n.id: set() for n in model.nodes}
        for edge in model.edges:
            if edge.source_id in adj and edge.target_id in adj:
                adj[edge.source_id].add(edge.target_id)
                adj[edge.target_id].add(edge.source_id)

        # Find a startEvent
        start_nodes = [n for n in model.nodes if n.element_type == "startEvent"]
        assert len(start_nodes) >= 1, "No startEvent found"
        start_id = start_nodes[0].id

        # BFS
        visited: set[str] = set()
        queue = deque([start_id])
        while queue:
            current = queue.popleft()
            if current in visited:
                continue
            visited.add(current)
            for neighbor in adj.get(current, set()):
                if neighbor not in visited:
                    queue.append(neighbor)

        all_node_ids = {n.id for n in model.nodes}
        unreachable = all_node_ids - visited
        assert not unreachable, (
            f"{example_process['name']}: {len(unreachable)} unreachable nodes: "
            f"{unreachable}"
        )

    def test_start_and_end_events_exist(self, example_process):
        """Every process must have at least 1 startEvent and 1 endEvent."""
        model = parse_bpmn(example_process["bpmn_path"])
        types = {n.element_type for n in model.nodes}
        assert "startEvent" in types, f"{example_process['name']}: no startEvent"
        assert "endEvent" in types, f"{example_process['name']}: no endEvent"

    def test_triple_count_matches(self, example_process):
        """Number of triple directories must equal expected total_triples."""
        triple_dirs = discover_triple_dirs(example_process["dir"])
        expected_count = example_process["expected"]["total_triples"]
        assert len(triple_dirs) == expected_count, (
            f"{example_process['name']}: expected {expected_count} triple dirs, "
            f"got {len(triple_dirs)}"
        )
