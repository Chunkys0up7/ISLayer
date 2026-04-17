"""Symbolic: consumer references path producer doesn't mention."""
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


def test_gap_ast(evaluator):
    prod = evaluator.parse("exists(borrower.name)")
    cons = evaluator.parse("exists(borrower.ssn)")
    r = SymbolicEvaluator().compare(prod, cons)
    assert r.verdict == SymbolicVerdict.UNDETERMINED
    assert "borrower.ssn" in r.gaps


def test_gap_assertions():
    prod = ContextAssertion(
        path="borrower.name", predicate=AssertionPredicate.EXISTS
    )
    cons = ContextAssertion(
        path="borrower.ssn", predicate=AssertionPredicate.EXISTS
    )
    r = SymbolicEvaluator().compare_assertions([prod], [cons])
    assert r.verdict == SymbolicVerdict.UNDETERMINED
    assert "borrower.ssn" in r.gaps


def test_gap_empty_producer():
    cons = ContextAssertion(
        path="borrower.ssn", predicate=AssertionPredicate.EXISTS
    )
    r = SymbolicEvaluator().compare_assertions([], [cons])
    assert r.verdict == SymbolicVerdict.UNDETERMINED
    assert "borrower.ssn" in r.gaps
