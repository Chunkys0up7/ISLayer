"""Compute the critical path node set.

Spec reference: files/03-journey-graph.md §B3

Sources in priority order:
  1. Explicit config: a caller-supplied list of bpmn_node_ids.
  2. Heuristic: BFS shortest path from every start_event to every
     end_event; union all such paths.
"""
from __future__ import annotations

from collections import deque
from typing import Optional

from triple_flow_sim.contracts import BpmnNodeType
from triple_flow_sim.components.c03_graph.bpmn_parser import BpmnGraphData


def compute_critical_path(
    bpmn_data: BpmnGraphData,
    config_nodes: Optional[list[str]] = None,
) -> set[str]:
    """Return the set of node ids considered on the critical path.

    If ``config_nodes`` is provided and non-empty, it wins and is returned
    verbatim (filtered to ids that actually exist). Otherwise, apply the
    BFS heuristic described in §B3.
    """
    if config_nodes:
        return {nid for nid in config_nodes if nid in bpmn_data.nodes}

    # Build a lightweight adjacency list from the edges.
    adjacency: dict[str, list[str]] = {nid: [] for nid in bpmn_data.nodes}
    for edge in bpmn_data.edges.values():
        if edge.source in adjacency and edge.target in bpmn_data.nodes:
            adjacency[edge.source].append(edge.target)

    starts = [
        nid for nid, n in bpmn_data.nodes.items()
        if n.node_type == BpmnNodeType.START_EVENT
    ]
    ends = {
        nid for nid, n in bpmn_data.nodes.items()
        if n.node_type == BpmnNodeType.END_EVENT
    }

    critical: set[str] = set()
    for start in starts:
        for end in ends:
            path = _bfs_shortest_path(adjacency, start, end)
            if path:
                critical.update(path)
    return critical


def _bfs_shortest_path(
    adjacency: dict[str, list[str]], start: str, goal: str
) -> Optional[list[str]]:
    """Plain BFS shortest path. Returns None if unreachable."""
    if start == goal:
        return [start]
    visited = {start}
    # queue holds (node, path_so_far)
    queue: deque[tuple[str, list[str]]] = deque([(start, [start])])
    while queue:
        node, path = queue.popleft()
        for nxt in adjacency.get(node, []):
            if nxt in visited:
                continue
            new_path = path + [nxt]
            if nxt == goal:
                return new_path
            visited.add(nxt)
            queue.append((nxt, new_path))
    return None
