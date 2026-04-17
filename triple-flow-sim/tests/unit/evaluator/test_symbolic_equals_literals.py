"""Symbolic: EQUALS with literal values."""
from __future__ import annotations

import pytest

from triple_flow_sim.contracts.triple import (
    AssertionPredicate,
    ContextAssertion,
)
from triple_flow_sim.evaluator import (
    ExpressionEvaluator,
    SymbolicEvaluator,
    SymbolicVerdict,
)


@pytest.fixture(scope="module")
def evaluator() -> ExpressionEvaluator:
    return ExpressionEvaluator()


def test_equals_same_literal_ast(evaluator):
    prod = evaluator.parse('decision.status == "approved"')
    cons = evaluator.parse('decision.status == "approved"')
    r = SymbolicEvaluator().compare(prod, cons)
    assert r.verdict == SymbolicVerdict.ALWAYS_SATISFIED


def test_equals_different_literal_ast(evaluator):
    prod = evaluator.parse('decision.status == "approved"')
    cons = evaluator.parse('decision.status == "rejected"')
    r = SymbolicEvaluator().compare(prod, cons)
    assert r.verdict == SymbolicVerdict.NEVER_SATISFIED
    assert "decision.status" in r.contradictions


def test_equals_assertions_match():
    prod = ContextAssertion(
        path="decision.status",
        predicate=AssertionPredicate.EQUALS,
        value="approved",
    )
    cons = ContextAssertion(
        path="decision.status",
        predicate=AssertionPredicate.EQUALS,
        value="approved",
    )
    r = SymbolicEvaluator().compare_assertions([prod], [cons])
    assert r.verdict == SymbolicVerdict.ALWAYS_SATISFIED


def test_equals_assertions_differ():
    prod = ContextAssertion(
        path="decision.status",
        predicate=AssertionPredicate.EQUALS,
        value="approved",
    )
    cons = ContextAssertion(
        path="decision.status",
        predicate=AssertionPredicate.EQUALS,
        value="rejected",
    )
    r = SymbolicEvaluator().compare_assertions([prod], [cons])
    assert r.verdict == SymbolicVerdict.NEVER_SATISFIED


def test_equals_producer_silent_undetermined():
    cons = ContextAssertion(
        path="decision.status",
        predicate=AssertionPredicate.EQUALS,
        value="approved",
    )
    r = SymbolicEvaluator().compare_assertions([], [cons])
    assert r.verdict == SymbolicVerdict.UNDETERMINED
    assert "decision.status" in r.gaps
