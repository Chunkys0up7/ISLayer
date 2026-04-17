"""Symbolic: malformed expressions should never crash."""
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


def test_producer_parse_failure(evaluator):
    r = evaluator.evaluate_symbolic("@@@ broken ###", "exists(x)")
    assert r.verdict == SymbolicVerdict.UNDETERMINED
    assert "producer" in r.reason.lower()


def test_consumer_parse_failure(evaluator):
    r = evaluator.evaluate_symbolic("exists(x)", "@@@ broken ###")
    assert r.verdict == SymbolicVerdict.UNDETERMINED
    assert "consumer" in r.reason.lower()


def test_both_empty(evaluator):
    r = evaluator.evaluate_symbolic("", "")
    assert r.verdict == SymbolicVerdict.UNDETERMINED


def test_producer_none(evaluator):
    r = evaluator.evaluate_symbolic(None, "exists(x)")
    assert r.verdict == SymbolicVerdict.UNDETERMINED


def test_assertion_satisfies_expression_parse_failure():
    prod = ContextAssertion(
        path="x",
        predicate=AssertionPredicate.SATISFIES_EXPRESSION,
        value="@@@ broken ###",
    )
    cons = ContextAssertion(
        path="x",
        predicate=AssertionPredicate.SATISFIES_EXPRESSION,
        value="@@@ also broken ###",
    )
    # Should not raise.
    r = SymbolicEvaluator().compare_assertions([prod], [cons])
    assert r.verdict == SymbolicVerdict.UNDETERMINED
