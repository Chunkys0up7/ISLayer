"""Gateway-level static checks G1-G3.

Spec reference: files/04-static-handoff-checker.md §B3
"""
from __future__ import annotations

from typing import Optional

from triple_flow_sim.contracts import (
    BpmnNodeType,
    Evidence,
    Generator,
    RawDetection,
    Triple,
)


def g1_evaluability(
    gateway_triple: Triple, evaluator
) -> list[RawDetection]:
    """Every decision_predicate's expression must parse. Unparseable ones
    emit an evaluability_gap signal (same signal type as inventory I9 — dedupe
    happens in the finding store).
    """
    detections: list[RawDetection] = []
    if gateway_triple.pim is None:
        return detections
    predicates = gateway_triple.pim.decision_predicates or []
    for bp in predicates:
        result = evaluator.validate(bp.predicate_expression or "")
        if result.ok:
            continue
        detections.append(
            RawDetection(
                signal_type="evaluability_gap",
                generator=Generator.STATIC_HANDOFF,
                primary_triple_id=gateway_triple.triple_id,
                bpmn_node_id=gateway_triple.bpmn_node_id,
                bpmn_edge_id=bp.edge_id,
                detector_context={
                    "expression": bp.predicate_expression,
                    "parse_error": result.error or "unknown",
                },
                evidence=Evidence(
                    observed=bp.predicate_expression,
                    expected="A parseable predicate expression",
                ),
            )
        )
    return detections


def g2_partitioning(
    gateway_triple: Triple, evaluator, symbolic
) -> list[RawDetection]:
    """For an exclusive gateway, check that no two predicates are
    simultaneously always-true (i.e., overlap). If overlapping and neither
    is marked is_default=True, emit predicate_non_partitioning.
    """
    detections: list[RawDetection] = []
    if gateway_triple.bpmn_node_type != BpmnNodeType.EXCLUSIVE_GATEWAY:
        return detections
    if gateway_triple.pim is None:
        return detections
    predicates = gateway_triple.pim.decision_predicates or []
    if len(predicates) < 2:
        return detections

    from triple_flow_sim.evaluator.symbolic import SymbolicVerdict

    # Pre-parse predicate expressions. Unparseable ones are skipped here —
    # G1 already reports them as evaluability_gap.
    asts: list = []
    for bp in predicates:
        result = evaluator.validate(bp.predicate_expression or "")
        asts.append(result.ast if result.ok else None)

    seen: set[tuple[int, int]] = set()
    for i, p1 in enumerate(predicates):
        for j, p2 in enumerate(predicates):
            if i >= j:
                continue
            if (i, j) in seen:
                continue
            seen.add((i, j))
            if asts[i] is None or asts[j] is None:
                continue
            # Overlap: treating p1 as producer and p2 as consumer; if
            # verdict is ALWAYS_SATISFIED then whenever p1 is true p2 is
            # also true — i.e., the two overlap (and if symmetric, they
            # are equivalent).
            r1 = symbolic.compare(asts[i], asts[j])
            r2 = symbolic.compare(asts[j], asts[i])
            v1 = getattr(r1, "verdict", r1)
            v2 = getattr(r2, "verdict", r2)
            if (
                v1 != SymbolicVerdict.ALWAYS_SATISFIED
                and v2 != SymbolicVerdict.ALWAYS_SATISFIED
            ):
                continue
            if p1.is_default or p2.is_default:
                continue
            detections.append(
                RawDetection(
                    signal_type="predicate_non_partitioning",
                    generator=Generator.STATIC_HANDOFF,
                    primary_triple_id=gateway_triple.triple_id,
                    bpmn_node_id=gateway_triple.bpmn_node_id,
                    detector_context={
                        "edge_a": p1.edge_id,
                        "edge_b": p2.edge_id,
                        "expression_a": p1.predicate_expression,
                        "expression_b": p2.predicate_expression,
                    },
                    evidence=Evidence(
                        observed=(
                            "Predicates overlap "
                            f"({p1.edge_id} vs {p2.edge_id})"
                        ),
                        expected=(
                            "Exclusive gateway predicates must be mutually "
                            "exclusive"
                        ),
                    ),
                )
            )
    return detections


def g3_coverage(gateway_triple: Triple) -> list[RawDetection]:
    """Gateway must cover all paths: either a ``is_default=True`` branch
    exists, or predicates are exhaustive. Without a default we cannot
    prove exhaustiveness in general, so we flag as branch_misdirection
    (medium confidence) to surface for SME review.
    """
    detections: list[RawDetection] = []
    if gateway_triple.bpmn_node_type != BpmnNodeType.EXCLUSIVE_GATEWAY:
        return detections
    if gateway_triple.pim is None:
        return detections
    predicates = gateway_triple.pim.decision_predicates or []
    if not predicates:
        return detections
    if any(bp.is_default for bp in predicates):
        return detections
    # No default branch — we can only prove exhaustiveness by structural
    # inspection of the expressions, which the stub symbolic evaluator cannot
    # do. Conservative rule: emit a branch_misdirection observation for SME
    # review.
    detections.append(
        RawDetection(
            signal_type="branch_misdirection",
            generator=Generator.STATIC_HANDOFF,
            primary_triple_id=gateway_triple.triple_id,
            bpmn_node_id=gateway_triple.bpmn_node_id,
            detector_context={
                "reason": "no_default_branch",
                "predicate_count": len(predicates),
            },
            evidence=Evidence(
                observed="No branch has is_default=True",
                expected=(
                    "Either a default branch or provably-exhaustive "
                    "predicates"
                ),
            ),
        )
    )
    return detections
