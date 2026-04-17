"""Symbolic: compound AND combinator rule.

Tie-breaking rule chosen: the worst (most restrictive) clause dominates.
    NEVER > SOMETIMES > UNDETERMINED > ALWAYS

So a consumer AND with one ALWAYS and one UNDETERMINED clause yields
UNDETERMINED (we cannot promise the unknown clause, so the conjunction
is unknown — never overclaim).
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


def test_and_all_always(evaluator):
    prod = evaluator.parse(
        "exists(borrower.income) and exists(borrower.name)"
    )
    cons = evaluator.parse(
        "exists(borrower.income) and exists(borrower.name)"
    )
    r = SymbolicEvaluator().compare(prod, cons)
    assert r.verdict == SymbolicVerdict.ALWAYS_SATISFIED


def test_and_one_always_one_undetermined(evaluator):
    # Producer guarantees income but not ssn; consumer needs both.
    prod = evaluator.parse("exists(borrower.income)")
    cons = evaluator.parse("exists(borrower.income) and exists(borrower.ssn)")
    r = SymbolicEvaluator().compare(prod, cons)
    # Tie-breaker: UNDETERMINED dominates ALWAYS under AND.
    assert r.verdict == SymbolicVerdict.UNDETERMINED
    assert "borrower.ssn" in r.gaps


def test_and_one_never_dominates(evaluator):
    prod = evaluator.parse(
        'exists(borrower.income) and status == "approved"'
    )
    cons = evaluator.parse(
        'exists(borrower.income) and status == "rejected"'
    )
    r = SymbolicEvaluator().compare(prod, cons)
    assert r.verdict == SymbolicVerdict.NEVER_SATISFIED


def test_and_assertions_one_always_one_undetermined():
    prod = [
        ContextAssertion(
            path="borrower.income", predicate=AssertionPredicate.EXISTS
        ),
    ]
    cons = [
        ContextAssertion(
            path="borrower.income", predicate=AssertionPredicate.EXISTS
        ),
        ContextAssertion(
            path="borrower.ssn", predicate=AssertionPredicate.EXISTS
        ),
    ]
    r = SymbolicEvaluator().compare_assertions(prod, cons)
    assert r.verdict == SymbolicVerdict.UNDETERMINED
    assert "borrower.ssn" in r.gaps


def test_or_any_always_wins(evaluator):
    prod = evaluator.parse("exists(borrower.income)")
    cons = evaluator.parse("exists(borrower.income) or exists(borrower.ssn)")
    r = SymbolicEvaluator().compare(prod, cons)
    assert r.verdict == SymbolicVerdict.ALWAYS_SATISFIED
