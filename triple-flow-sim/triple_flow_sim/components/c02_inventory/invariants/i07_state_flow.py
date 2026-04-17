"""Invariant I7 — every read path must be written by some triple.

Phase 1 implementation uses the "any writer anywhere" check. When a graph is
provided, reachability filtering (`is_reachable(writer_node, reader_node)`) is
available but is left as a later refinement; see spec files/03-journey-graph.md.

Spec: files/triple-schema.md §I7
"""
from __future__ import annotations

from triple_flow_sim.contracts import (
    Evidence,
    Generator,
    RawDetection,
    TripleSet,
)


def _paths_from(collection) -> list[str]:
    """Extract .path strings from a StateFieldRef / ContextAssertion list."""
    if not collection:
        return []
    out = []
    for item in collection:
        path = getattr(item, "path", None)
        if path:
            out.append(path)
    return out


def check(triple_set: TripleSet, graph=None) -> list[RawDetection]:
    # Build global writer map: path -> list of (triple_id, bpmn_node_id)
    writer_map: dict[str, list[tuple[str, str]]] = {}
    for triple in triple_set.triples.values():
        if triple.pim is None:
            continue
        writes = _paths_from(triple.pim.state_writes) + _paths_from(triple.pim.postconditions)
        for path in writes:
            writer_map.setdefault(path, []).append(
                (triple.triple_id, triple.bpmn_node_id)
            )

    detections: list[RawDetection] = []
    for triple in triple_set.triples.values():
        if triple.pim is None:
            continue
        reads = _paths_from(triple.pim.state_reads) + _paths_from(triple.pim.preconditions)
        for path in reads:
            writers = writer_map.get(path, [])

            if not writers:
                # Nothing anywhere writes this path
                detections.append(RawDetection(
                    signal_type="state_flow_gap",
                    generator=Generator.INVENTORY,
                    primary_triple_id=triple.triple_id or "<unnamed>",
                    bpmn_node_id=triple.bpmn_node_id or None,
                    detector_context={"path": path},
                    evidence=Evidence(
                        observed=f"no writer for '{path}'",
                        expected=f"some upstream triple writes '{path}'",
                    ),
                ))
                continue

            # If graph is provided, perform reachability filter.
            if graph is not None and triple.bpmn_node_id:
                reader_node = triple.bpmn_node_id
                reachable_writer = False
                for writer_tid, writer_node in writers:
                    if writer_tid == triple.triple_id:
                        # Self-write doesn't count as upstream for a read
                        continue
                    if not writer_node:
                        # Unknown writer node — treat as satisfying the global check
                        reachable_writer = True
                        break
                    try:
                        if graph.is_reachable(writer_node, reader_node):
                            reachable_writer = True
                            break
                    except Exception:
                        # Graph method may be missing — fall back to global
                        reachable_writer = True
                        break
                if not reachable_writer:
                    detections.append(RawDetection(
                        signal_type="state_flow_gap",
                        generator=Generator.INVENTORY,
                        primary_triple_id=triple.triple_id or "<unnamed>",
                        bpmn_node_id=triple.bpmn_node_id or None,
                        detector_context={"path": path},
                        evidence=Evidence(
                            observed=f"no upstream-reachable writer for '{path}'",
                            expected=f"a writer on an upstream path to {reader_node}",
                        ),
                    ))
    return detections
