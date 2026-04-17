# Component 03 — Journey Graph

## Purpose

Build a traversable graph representation of the BPMN process where each node is bound to its corresponding triple. This graph is the substrate that every simulation component operates over: static handoff checks traverse edges, sequence runners walk from start to end, isolation harness examines specific pairs.

## Inputs

- `TripleSet` (preferably `SimulationReadySet` from component 02).
- One of:
  - A BPMN XML file (authoritative source, preferred).
  - A derived topology reconstructed from triples' `bpmn_node_id` and the edges implied by their `pim.preconditions.source_triple` references.

If both are available, BPMN XML is authoritative; triple-derived topology is used for cross-validation and produces findings where they disagree.

## Outputs

- `JourneyGraph` object: a directed graph with:
  - Nodes indexed by `bpmn_node_id`, each carrying:
    - Bound triple (may be None for unbound nodes → `orphan_triple` finding emitted)
    - BPMN node type
    - Position metadata (for reporting)
    - `is_on_critical_path: bool` — marks happy-path nodes
  - Edges with:
    - `edge_id`
    - `source_node_id`, `target_node_id`
    - `predicate?` — for gateway outgoing edges, the evaluable expression
    - `is_default_branch: bool`
- `GraphReport` — graph-level findings and statistics:
  - Number of start/end events, tasks, gateways
  - Unreachable nodes (no path from any start event)
  - Nodes with no outgoing edges other than end events
  - Loops detected and whether they have documented exit conditions
  - Disagreements between BPMN XML and triple-derived topology

## Behavior

### B1. Parse BPMN source

Parse BPMN 2.0 XML into nodes and edges. Preserve original IDs. Use a standard BPMN library (e.g., `xml.etree` with BPMN namespaces, or `bpmn-python`).

### B2. Bind triples to nodes

For each node, look up a triple by `bpmn_node_id` in the TripleSet. Record binding. Unbound nodes → `orphan_triple` finding. Triples in the TripleSet not matching any node → also `orphan_triple` (triple orphan, not node orphan).

### B3. Mark critical path

The "critical path" is the canonical happy-path through the process. Sources (in priority order):
1. Explicit BPMN annotation if present (`happyPath` marker).
2. Configuration file listing node IDs on the critical path.
3. Heuristic: for each gateway, identify the branch that leads to the primary success end event with the shortest path. (Heuristic is a fallback; log that it was used.)

Mark each node `is_on_critical_path`. This feeds into blast radius calculation in the finding store.

### B4. Build derived topology (cross-validation)

Independently of the BPMN, construct a topology from triples:
- For each triple, examine `pim.preconditions[*].source_triple` fields.
- Build edges: for each precondition with a source_triple, add edge from `source_triple.bpmn_node_id` to this triple's `bpmn_node_id`.

### B5. Compare topologies

Cross-check:
- Edges in BPMN but not in derived topology → triples may be missing `source_triple` attributions. Finding: `state_flow_gap` candidate.
- Edges in derived topology but not in BPMN → triples reference predecessors the BPMN doesn't connect. Finding: structural inconsistency, severity `correctness`.
- Log disagreements in GraphReport.

### B6. Detect structural issues

- **Unreachable nodes:** no path from any start event. Finding: `orphan_triple` on the bound triple if any.
- **Dead ends:** non-end-event nodes with no outgoing edges. Finding: structural inconsistency.
- **Unbounded loops:** cycles in the graph. For each cycle, verify at least one node has an obligation or predicate that can terminate the loop; if not → finding: `journey_stuck` risk.
- **Gateway fan-out validation:** every exclusive gateway must have ≥2 outgoing edges; every parallel gateway's outgoing edges must all be reachable.

### B7. Expose traversal API

Provide methods the simulation components need:

```python
class JourneyGraph:
    def start_events(self) -> list[Node]: ...
    def end_events(self) -> list[Node]: ...
    def successors(self, node_id: str) -> list[Node]: ...
    def predecessors(self, node_id: str) -> list[Node]: ...
    def edges_from(self, node_id: str) -> list[Edge]: ...
    def all_paths(self, from_node: str, to_node: str, max_depth: int = 100) -> list[list[str]]: ...
    def is_reachable(self, from_node: str, to_node: str) -> bool: ...
    def pairs_to_check(self) -> list[tuple[str, str]]: ...   # All (producer, consumer) pairs for handoff checking
    def get_triple(self, node_id: str) -> Triple: ...
    def get_node(self, node_id: str) -> Node: ...
```

## What this component does NOT do

- Does not execute triples.
- Does not evaluate predicates — it stores them as strings and the evaluator is component 04.
- Does not modify the BPMN or triples.
- Does not determine journey outcomes.

## Dependencies

- Component 01 (Triple Loader).
- Component 02 (Triple Inventory) — produces SimulationReadySet. Can run without inventory in early builds, but findings may be duplicated.
- `contracts/triple-schema.md`.
- BPMN source (XML).

## Verification

**V1.** On a simple 5-node BPMN (start → task → gateway → task → end) with all triples bound, graph has 5 nodes, 4 edges (plus gateway branches), zero findings.

**V2.** Add an unreferenced BPMN node: graph reports it as unreachable or orphan.

**V3.** Add a triple with `bpmn_node_id` matching no BPMN node: graph reports it as orphan triple.

**V4.** Introduce a cycle with no termination condition: graph reports loop risk.

**V5.** Construct a BPMN with a gateway node and a triple missing `source_triple` attribution upstream: cross-validation reports the attribution gap.

**V6.** `pairs_to_check()` returns every (u, v) where v is a direct successor of u in the graph.

## Implementation notes

- Use NetworkX for graph storage — well-understood, fast, and `all_paths` / reachability come for free.
- Cache path computations for large graphs.
- Serialize the graph to DOT or similar for visual debugging; very useful for SME review.
- Keep BPMN parsing isolated in one module; support both BPMN 2.0 XML and a simplified JSON format for test fixtures.
- The `pairs_to_check` method is called heavily by component 04 — make sure it's computed once and cached.
