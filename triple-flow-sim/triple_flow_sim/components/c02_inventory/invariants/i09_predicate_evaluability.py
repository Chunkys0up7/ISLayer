"""Invariant I9 — gateway decision_predicates parse cleanly.

Spec: files/triple-schema.md §I9
"""
from __future__ import annotations

from triple_flow_sim.contracts import (
    BpmnNodeType,
    Evidence,
    Generator,
    RawDetection,
    TripleSet,
)
from triple_flow_sim.evaluator import ExpressionEvaluator


_GATEWAY_TYPES = {BpmnNodeType.EXCLUSIVE_GATEWAY, BpmnNodeType.PARALLEL_GATEWAY}


def check(triple_set: TripleSet, graph=None) -> list[RawDetection]:
    detections: list[RawDetection] = []
    try:
        evaluator = ExpressionEvaluator()
    except Exception as exc:  # noqa: BLE001
        # Evaluator construction should not fail, but if it does we can't check.
        return [RawDetection(
            signal_type="unparseable_predicate",
            generator=Generator.INVENTORY,
            primary_triple_id="<evaluator>",
            detector_context={
                "expression": "",
                "parse_error": f"Evaluator init failed: {exc}",
            },
            evidence=Evidence(observed=str(exc), expected="working evaluator"),
        )]

    for triple in triple_set.triples.values():
        if triple.bpmn_node_type not in _GATEWAY_TYPES:
            continue
        if triple.pim is None:
            continue
        predicates = triple.pim.decision_predicates or []
        for pred in predicates:
            expr = getattr(pred, "predicate_expression", "") or ""
            edge_id = getattr(pred, "edge_id", None)
            result = evaluator.validate(expr)
            if not result.ok:
                detections.append(RawDetection(
                    signal_type="unparseable_predicate",
                    generator=Generator.INVENTORY,
                    primary_triple_id=triple.triple_id or "<unnamed>",
                    bpmn_node_id=triple.bpmn_node_id or None,
                    bpmn_edge_id=edge_id,
                    detector_context={
                        "expression": expr,
                        "parse_error": result.error or "",
                    },
                    evidence=Evidence(
                        observed=expr,
                        expected="parseable predicate expression",
                    ),
                ))
    return detections
