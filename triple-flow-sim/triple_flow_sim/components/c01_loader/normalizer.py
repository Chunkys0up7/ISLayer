"""Post-processing normalization for loaded Triples.

Spec reference: files/01-triple-loader.md §B5-B6.
"""
from __future__ import annotations

from triple_flow_sim.contracts.triple import Triple


def validate_identity(triple: Triple) -> list[str]:
    """Returns list of missing required identity fields. Empty = passes I1.

    Per files/triple-schema.md §I1, the required identity fields are:
      triple_id, version, bpmn_node_id. bpmn_node_type has an enum default.
    """
    missing: list[str] = []
    if not triple.triple_id:
        missing.append("triple_id")
    if not triple.version:
        missing.append("version")
    if not triple.bpmn_node_id:
        missing.append("bpmn_node_id")
    return missing


def normalize(triple: Triple) -> Triple:
    """Strip trailing whitespace on string scalars and apply minor cleanup.

    Preserves None on optional Optional[list] fields so downstream invariants
    (I4 contract_missing / I7 state_flow_gap) can still fire.
    """
    if isinstance(triple.triple_id, str):
        triple.triple_id = triple.triple_id.strip()
    if isinstance(triple.version, str):
        triple.version = triple.version.strip()
    if isinstance(triple.bpmn_node_id, str):
        triple.bpmn_node_id = triple.bpmn_node_id.strip()
    if triple.cim is not None and isinstance(triple.cim.intent, str):
        triple.cim.intent = triple.cim.intent.strip()
    return triple
