"""Gateway checks G1, G2, G3."""
from __future__ import annotations

from triple_flow_sim.components.c04_static_handoff import gateway_checks
from triple_flow_sim.contracts import BpmnNodeType, BranchPredicate
from triple_flow_sim.evaluator.parser import ExpressionEvaluator
from triple_flow_sim.evaluator.symbolic import SymbolicEvaluator

from .conftest import make_triple


def test_g1_flags_unparseable_predicate():
    gw = make_triple(
        "t-gw", "GW_1",
        node_type=BpmnNodeType.EXCLUSIVE_GATEWAY,
        decision_predicates=[
            BranchPredicate(
                edge_id="e_bad",
                predicate_expression="???NOT A VALID EXPR???",
            ),
            BranchPredicate(
                edge_id="e_ok",
                predicate_expression="x == 1",
            ),
        ],
    )
    ev = ExpressionEvaluator()
    detections = gateway_checks.g1_evaluability(gw, ev)
    signal_types = [d.signal_type for d in detections]
    assert "evaluability_gap" in signal_types
    assert len([d for d in detections if d.signal_type == "evaluability_gap"]) == 1


def test_g2_flags_overlapping_identical_predicates():
    # Two identical non-trivial predicates are provably equivalent — the
    # symbolic evaluator returns ALWAYS_SATISFIED in both directions, so
    # G2 must flag non-partitioning.
    gw = make_triple(
        "t-gw", "GW_1",
        node_type=BpmnNodeType.EXCLUSIVE_GATEWAY,
        decision_predicates=[
            BranchPredicate(edge_id="e1", predicate_expression="x == 1"),
            BranchPredicate(edge_id="e2", predicate_expression="x == 1"),
        ],
    )
    ev = ExpressionEvaluator()
    sym = SymbolicEvaluator()
    detections = gateway_checks.g2_partitioning(gw, ev, sym)
    assert any(d.signal_type == "predicate_non_partitioning" for d in detections)


def test_g3_flags_gateway_with_no_default():
    gw = make_triple(
        "t-gw", "GW_1",
        node_type=BpmnNodeType.EXCLUSIVE_GATEWAY,
        decision_predicates=[
            BranchPredicate(edge_id="e1", predicate_expression="x == 1"),
            BranchPredicate(edge_id="e2", predicate_expression="x == 2"),
        ],
    )
    detections = gateway_checks.g3_coverage(gw)
    assert len(detections) == 1
    assert detections[0].signal_type == "branch_misdirection"


def test_g3_no_detection_when_default_branch_exists():
    gw = make_triple(
        "t-gw", "GW_1",
        node_type=BpmnNodeType.EXCLUSIVE_GATEWAY,
        decision_predicates=[
            BranchPredicate(edge_id="e1", predicate_expression="x == 1"),
            BranchPredicate(
                edge_id="e_default",
                predicate_expression="true",
                is_default=True,
            ),
        ],
    )
    detections = gateway_checks.g3_coverage(gw)
    assert detections == []
