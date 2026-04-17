"""Completeness matrix: per-triple field presence map.

Spec: files/02-triple-inventory.md §Completeness matrix
"""
from __future__ import annotations

from triple_flow_sim.contracts import Triple, TripleSet

FIELDS_TO_CHECK = [
    # (dotted_path, type: 'required' | 'optional' | 'conditional')
    ("triple_id", "required"),
    ("version", "required"),
    ("bpmn_node_id", "required"),
    ("bpmn_node_type", "required"),
    ("cim.intent", "required"),
    ("cim.regulatory_refs", "optional"),
    ("cim.business_rules", "optional"),
    ("pim.preconditions", "required"),
    ("pim.postconditions", "required"),
    ("pim.obligations_opened", "optional"),
    ("pim.obligations_closed", "optional"),
    ("pim.decision_predicates", "conditional"),  # Required for gateways
    ("pim.state_reads", "required"),
    ("pim.state_writes", "required"),
    ("psm.enriched_content", "required"),
    ("psm.prompt_scaffold", "optional"),
    ("psm.tool_bindings", "optional"),
]


def check_field(triple: Triple, dotted_path: str) -> str:
    """Returns '+' (present+non-empty), 'o' (present+empty), or '-' (missing).

    Uses ASCII markers for universal terminal compatibility.
    """
    segments = dotted_path.split(".")
    obj = triple
    for seg in segments:
        if obj is None:
            return "-"
        obj = getattr(obj, seg, None)
    if obj is None:
        return "-"
    if isinstance(obj, (list, dict, str)) and len(obj) == 0:
        return "o"
    return "+"


def build_matrix(triple_set: TripleSet) -> dict:
    """Returns {triple_id: {field_path: marker}} matrix."""
    matrix: dict[str, dict[str, str]] = {}
    for triple_id, triple in triple_set.triples.items():
        matrix[triple_id] = {
            path: check_field(triple, path) for path, _type in FIELDS_TO_CHECK
        }
    return matrix


def render_markdown(matrix: dict) -> str:
    """Render matrix as markdown table."""
    if not matrix:
        return "*(no triples)*"
    fields = [p for p, _ in FIELDS_TO_CHECK]
    header = "| triple_id | " + " | ".join(fields) + " |"
    sep = "|" + "|".join(["---"] * (len(fields) + 1)) + "|"
    rows = [header, sep]
    for triple_id in sorted(matrix.keys()):
        cells = [triple_id] + [matrix[triple_id][f] for f in fields]
        rows.append("| " + " | ".join(cells) + " |")
    return "\n".join(rows)
