"""Symbolic: NOT swaps ALWAYS and NEVER."""
from __future__ import annotations

import pytest

from triple_flow_sim.evaluator import (
    ExpressionEvaluator,
    SymbolicEvaluator,
    SymbolicVerdict,
)


@pytest.fixture(scope="module")
def evaluator() -> ExpressionEvaluator:
    return ExpressionEvaluator()


def test_not_always_becomes_never(evaluator):
    # Without NOT, this would be ALWAYS_SATISFIED.
    prod = evaluator.parse("exists(borrower.income)")
    cons = evaluator.parse("not exists(borrower.income)")
    r = SymbolicEvaluator().compare(prod, cons)
    assert r.verdict == SymbolicVerdict.NEVER_SATISFIED


def test_not_undetermined_stays_undetermined(evaluator):
    prod = evaluator.parse("exists(borrower.name)")
    cons = evaluator.parse("not exists(borrower.ssn)")
    r = SymbolicEvaluator().compare(prod, cons)
    assert r.verdict == SymbolicVerdict.UNDETERMINED


def test_not_sometimes_stays_sometimes(evaluator):
    prod = evaluator.parse("in_range(credit.score, 550, 700)")
    cons = evaluator.parse("not in_range(credit.score, 600, 850)")
    r = SymbolicEvaluator().compare(prod, cons)
    assert r.verdict == SymbolicVerdict.SOMETIMES_SATISFIED


def test_double_negation(evaluator):
    prod = evaluator.parse("exists(borrower.income)")
    cons = evaluator.parse("not (not exists(borrower.income))")
    r = SymbolicEvaluator().compare(prod, cons)
    assert r.verdict == SymbolicVerdict.ALWAYS_SATISFIED
