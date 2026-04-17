"""Symbolic: IN_RANGE subset / disjoint / overlap."""
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


def test_range_subset_always(evaluator):
    prod = evaluator.parse("in_range(credit.score, 700, 800)")
    cons = evaluator.parse("in_range(credit.score, 600, 850)")
    r = SymbolicEvaluator().compare(prod, cons)
    assert r.verdict == SymbolicVerdict.ALWAYS_SATISFIED


def test_range_disjoint_never(evaluator):
    prod = evaluator.parse("in_range(credit.score, 300, 500)")
    cons = evaluator.parse("in_range(credit.score, 600, 850)")
    r = SymbolicEvaluator().compare(prod, cons)
    assert r.verdict == SymbolicVerdict.NEVER_SATISFIED
    assert "credit.score" in r.contradictions


def test_range_overlap_sometimes(evaluator):
    prod = evaluator.parse("in_range(credit.score, 550, 700)")
    cons = evaluator.parse("in_range(credit.score, 600, 850)")
    r = SymbolicEvaluator().compare(prod, cons)
    assert r.verdict == SymbolicVerdict.SOMETIMES_SATISFIED


def test_range_assertions_subset():
    prod = ContextAssertion(
        path="credit.score",
        predicate=AssertionPredicate.IN_RANGE,
        value=[700, 800],
    )
    cons = ContextAssertion(
        path="credit.score",
        predicate=AssertionPredicate.IN_RANGE,
        value=[600, 850],
    )
    r = SymbolicEvaluator().compare_assertions([prod], [cons])
    assert r.verdict == SymbolicVerdict.ALWAYS_SATISFIED


def test_range_assertions_disjoint():
    prod = ContextAssertion(
        path="credit.score",
        predicate=AssertionPredicate.IN_RANGE,
        value=[300, 500],
    )
    cons = ContextAssertion(
        path="credit.score",
        predicate=AssertionPredicate.IN_RANGE,
        value=[600, 850],
    )
    r = SymbolicEvaluator().compare_assertions([prod], [cons])
    assert r.verdict == SymbolicVerdict.NEVER_SATISFIED


def test_range_assertions_overlap():
    prod = ContextAssertion(
        path="credit.score",
        predicate=AssertionPredicate.IN_RANGE,
        value=[550, 700],
    )
    cons = ContextAssertion(
        path="credit.score",
        predicate=AssertionPredicate.IN_RANGE,
        value=[600, 850],
    )
    r = SymbolicEvaluator().compare_assertions([prod], [cons])
    assert r.verdict == SymbolicVerdict.SOMETIMES_SATISFIED
