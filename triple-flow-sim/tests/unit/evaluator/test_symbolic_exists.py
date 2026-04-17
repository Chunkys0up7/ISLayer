"""Symbolic: exists(path) producer vs consumer.

Spec reference: files/04-static-handoff-checker.md §B4.
"""
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


def test_exists_ast_always_satisfied(evaluator):
    prod = evaluator.parse("exists(borrower.income)")
    cons = evaluator.parse("exists(borrower.income)")
    result = SymbolicEvaluator().compare(prod, cons)
    assert result.verdict == SymbolicVerdict.ALWAYS_SATISFIED
    assert "borrower.income" in result.overlaps


def test_exists_via_evaluate_symbolic(evaluator):
    r = evaluator.evaluate_symbolic(
        "exists(borrower.income)", "exists(borrower.income)"
    )
    assert r.verdict == SymbolicVerdict.ALWAYS_SATISFIED


def test_exists_producer_silent_undetermined():
    prod = ContextAssertion(
        path="other.field", predicate=AssertionPredicate.EXISTS
    )
    cons = ContextAssertion(
        path="borrower.income", predicate=AssertionPredicate.EXISTS
    )
    r = SymbolicEvaluator().compare_assertions([prod], [cons])
    assert r.verdict == SymbolicVerdict.UNDETERMINED
    assert "borrower.income" in r.gaps


def test_exists_assertion_always_satisfied():
    prod = ContextAssertion(
        path="borrower.income", predicate=AssertionPredicate.EXISTS
    )
    cons = ContextAssertion(
        path="borrower.income", predicate=AssertionPredicate.EXISTS
    )
    r = SymbolicEvaluator().compare_assertions([prod], [cons])
    assert r.verdict == SymbolicVerdict.ALWAYS_SATISFIED


def test_exists_vs_is_empty_never(evaluator):
    prod = evaluator.parse("is_empty(borrower.income)")
    cons = evaluator.parse("exists(borrower.income)")
    r = SymbolicEvaluator().compare(prod, cons)
    assert r.verdict == SymbolicVerdict.NEVER_SATISFIED
    assert "borrower.income" in r.contradictions
