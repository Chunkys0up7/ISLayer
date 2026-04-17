"""JourneyGraph — traversable BPMN graph with triple bindings.

Spec reference: files/03-journey-graph.md §B6, §B7

Phase 1 scope:
  - B1: BPMN parse (bpmn_parser)
  - B2: Triple binding (binder)
  - B3: Critical path (critical_path)
  - B6: Structural checks (unreachable nodes, dead ends)
  - B7: Traversal API

Deferred to Phase 2: B4 (derived topology), B5 (cross-validation),
parallel gateway semantics.
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional

import networkx as nx

from triple_flow_sim.contracts import (
    BpmnNodeType,
    Evidence,
    Generator,
    RawDetection,
    Triple,
    TripleSet,
)
from triple_flow_sim.components.c03_graph.binder import bind
from triple_flow_sim.components.c03_graph.bpmn_parser import (
    BpmnEdgeDef,
    BpmnGraphData,
    BpmnNodeDef,
    parse_bpmn,
)
from triple_flow_sim.components.c03_graph.critical_path import compute_critical_path
from triple_flow_sim.components.c03_graph.cross_validation import cross_validate
from triple_flow_sim.components.c03_graph.derived_topology import (
    build_derived_topology,
    derive_detections,
)
from triple_flow_sim.components.c03_graph.loop_detection import (
    detect_unbounded_loops,
    find_loops,
)


class JourneyGraph:
    """Triples + BPMN, fused into a traversable graph with detections."""

    # ------------------------------------------------------------------
    # Construction
    # ------------------------------------------------------------------
    def __init__(
        self,
        bpmn_data: BpmnGraphData,
        triple_set: TripleSet,
        critical_path_ids: Optional[set[str]] = None,
    ):
        self._bpmn = bpmn_data
        self._triples = triple_set
        self._bindings, binding_detections = bind(triple_set, bpmn_data)
        self._critical_path: set[str] = set(critical_path_ids or set())
        self._detections: list[RawDetection] = list(binding_detections)
        self._nx = self._build_networkx()
        self._detections.extend(self._structural_checks())

    @classmethod
    def from_bpmn_file(
        cls,
        bpmn_path: Path,
        triple_set: TripleSet,
        config_critical_path: Optional[list[str]] = None,
    ) -> "JourneyGraph":
        bpmn_data = parse_bpmn(bpmn_path)
        crit = compute_critical_path(bpmn_data, config_critical_path or [])
        return cls(bpmn_data, triple_set, crit)

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------
    def _build_networkx(self) -> nx.DiGraph:
        G: nx.DiGraph = nx.DiGraph()
        for node_id, node in self._bpmn.nodes.items():
            G.add_node(
                node_id,
                node_type=node.node_type,
                name=node.name,
                lane=node.lane,
                is_on_critical_path=(node_id in self._critical_path),
                triple=self._bindings.get(node_id),
            )
        for edge_id, edge in self._bpmn.edges.items():
            if edge.source not in G.nodes or edge.target not in G.nodes:
                continue
            G.add_edge(
                edge.source,
                edge.target,
                edge_id=edge_id,
                condition=edge.condition,
                is_default=edge.is_default,
                name=edge.name,
            )
        return G

    def _structural_checks(self) -> list[RawDetection]:
        """Detect unreachable nodes and dead ends (§B6).

        Emits ``orphan_triple`` with a ``reason`` discriminator in
        ``detector_context`` so downstream classification can distinguish
        ``unreachable_from_start`` vs. ``dead_end``.
        """
        detections: list[RawDetection] = []
        starts = [
            n for n, d in self._nx.nodes(data=True)
            if d["node_type"] == BpmnNodeType.START_EVENT
        ]
        # Reachability check only makes sense when at least one start exists.
        if starts:
            reachable: set[str] = set()
            for s in starts:
                reachable.add(s)
                reachable.update(nx.descendants(self._nx, s))
            for node_id, node_data in self._nx.nodes(data=True):
                if node_id in reachable:
                    continue
                triple = node_data.get("triple")
                if triple is None:
                    continue  # handled separately via orphan_bpmn_node
                detections.append(
                    RawDetection(
                        signal_type="orphan_triple",
                        generator=Generator.INVENTORY,
                        primary_triple_id=triple.triple_id,
                        bpmn_node_id=node_id,
                        detector_context={"reason": "unreachable_from_start"},
                        evidence=Evidence(
                            observed=(
                                f"Node {node_id} has no path from any "
                                f"start_event"
                            )
                        ),
                    )
                )

        # Dead ends: non-end-event nodes with no outgoing edges.
        for node_id, node_data in self._nx.nodes(data=True):
            if node_data["node_type"] == BpmnNodeType.END_EVENT:
                continue
            if self._nx.out_degree(node_id) != 0:
                continue
            triple = node_data.get("triple")
            if triple is None:
                continue
            detections.append(
                RawDetection(
                    signal_type="orphan_triple",
                    generator=Generator.INVENTORY,
                    primary_triple_id=triple.triple_id,
                    bpmn_node_id=node_id,
                    detector_context={"reason": "dead_end"},
                    evidence=Evidence(
                        observed=(
                            f"Node {node_id} has no outgoing edges but is "
                            f"not an end event"
                        )
                    ),
                )
            )
        return detections

    # ------------------------------------------------------------------
    # Traversal API (§B7)
    # ------------------------------------------------------------------
    def start_events(self) -> list[str]:
        return [
            n for n, d in self._nx.nodes(data=True)
            if d["node_type"] == BpmnNodeType.START_EVENT
        ]

    def end_events(self) -> list[str]:
        return [
            n for n, d in self._nx.nodes(data=True)
            if d["node_type"] == BpmnNodeType.END_EVENT
        ]

    def successors(self, node_id: str) -> list[str]:
        if node_id not in self._nx.nodes:
            return []
        return list(self._nx.successors(node_id))

    def predecessors(self, node_id: str) -> list[str]:
        if node_id not in self._nx.nodes:
            return []
        return list(self._nx.predecessors(node_id))

    def edges_from(self, node_id: str) -> list[dict]:
        """[{edge_id, target, condition, is_default, name}] for node_id."""
        if node_id not in self._nx.nodes:
            return []
        out: list[dict] = []
        for tgt in self._nx.successors(node_id):
            data = self._nx.get_edge_data(node_id, tgt) or {}
            out.append(
                {
                    "edge_id": data.get("edge_id"),
                    "target": tgt,
                    "condition": data.get("condition"),
                    "is_default": data.get("is_default", False),
                    "name": data.get("name"),
                }
            )
        return out

    def is_reachable(self, from_node: str, to_node: str) -> bool:
        if from_node not in self._nx.nodes or to_node not in self._nx.nodes:
            return False
        return nx.has_path(self._nx, from_node, to_node)

    def all_paths(
        self, from_node: str, to_node: str, max_depth: int = 100
    ) -> list[list[str]]:
        if from_node not in self._nx.nodes or to_node not in self._nx.nodes:
            return []
        try:
            return list(
                nx.all_simple_paths(
                    self._nx, from_node, to_node, cutoff=max_depth
                )
            )
        except nx.NetworkXNoPath:
            return []

    def pairs_to_check(self) -> list[tuple[str, str]]:
        """All (producer, consumer) pairs where consumer is a direct successor."""
        return [(u, v) for u, v in self._nx.edges()]

    def get_triple(self, node_id: str) -> Optional[Triple]:
        return self._bindings.get(node_id)

    def get_node(self, node_id: str) -> Optional[dict]:
        if node_id not in self._nx.nodes:
            return None
        return dict(self._nx.nodes[node_id])

    def is_on_critical_path(self, node_id: str) -> bool:
        return node_id in self._critical_path

    # ------------------------------------------------------------------
    # Phase 2 additions: derived topology, cross-validation, loops (§B4, §B5)
    # ------------------------------------------------------------------
    def get_derived_topology(self) -> nx.DiGraph:
        """Return the triple-contract-derived topology (producer → consumer)."""
        return build_derived_topology(self._triples)

    def derive_topology_detections(self) -> list[RawDetection]:
        """Detections visible from the derived topology alone
        (missing producers, self-references)."""
        return derive_detections(self._triples)

    def cross_validate_against_derived(self) -> list[RawDetection]:
        """Compare BPMN edges to derived-topology edges (§B5)."""
        derived = self.get_derived_topology()
        return cross_validate(self, derived)

    def find_unbounded_loops(self) -> list[RawDetection]:
        """Emit detections for every simple cycle without an exit gateway."""
        return detect_unbounded_loops(self._nx, self._triples)

    def all_cycles(self) -> list[list[str]]:
        """Raw list of simple cycles (node-id lists)."""
        return find_loops(self._nx)

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------
    @property
    def detections(self) -> list[RawDetection]:
        return list(self._detections)

    @property
    def bpmn_data(self) -> BpmnGraphData:
        return self._bpmn

    @property
    def bindings(self) -> dict[str, Triple]:
        return dict(self._bindings)

    @property
    def critical_path(self) -> set[str]:
        return set(self._critical_path)

    @property
    def networkx(self) -> nx.DiGraph:
        return self._nx
