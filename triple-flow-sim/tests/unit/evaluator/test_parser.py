"""Unit tests for the expression parser (Phase 1, parse-only).

Spec reference: files/04-static-handoff-checker.md §B4
"""
from __future__ import annotations

import pytest

from triple_flow_sim.evaluator import (
    BoolOp,
    Compare,
    ExpressionEvaluator,
    FuncCall,
    InOp,
    ListLiteral,
    Literal,
    NotOp,
    PathRef,
)


@pytest.fixture(scope="module")
def evaluator() -> ExpressionEvaluator:
    return ExpressionEvaluator()


# ---------------------------------------------------------------------------
# Valid expressions
# ---------------------------------------------------------------------------
def test_simple_bool_equality(evaluator):
    result = evaluator.validate("borrower.verified == true")
    assert result.ok, result.error
    assert isinstance(result.ast, Compare)
    assert result.ast.op == "=="
    assert isinstance(result.ast.left, PathRef)
    assert result.ast.left.dotted == "borrower.verified"
    assert isinstance(result.ast.right, Literal)
    assert result.ast.right.value is True


def test_numeric_gte(evaluator):
    result = evaluator.validate("amount >= 1000")
    assert result.ok, result.error
    assert isinstance(result.ast, Compare)
    assert result.ast.op == ">="
    assert isinstance(result.ast.left, PathRef)
    assert result.ast.left.dotted == "amount"
    assert isinstance(result.ast.right, Literal)
    assert result.ast.right.value == 1000
    assert result.ast.right.type_hint == "int"


def test_in_list_strings(evaluator):
    result = evaluator.validate('status in ["approved", "complete"]')
    assert result.ok, result.error
    assert isinstance(result.ast, InOp)
    assert result.ast.negated is False
    assert isinstance(result.ast.member, PathRef)
    assert result.ast.member.dotted == "status"
    assert isinstance(result.ast.container, ListLiteral)
    assert len(result.ast.container.items) == 2
    assert all(isinstance(it, Literal) for it in result.ast.container.items)
    assert [it.value for it in result.ast.container.items] == ["approved", "complete"]


def test_not_in_list_ints(evaluator):
    result = evaluator.validate("state not in [1, 2, 3]")
    assert result.ok, result.error
    assert isinstance(result.ast, InOp)
    assert result.ast.negated is True
    assert isinstance(result.ast.container, ListLiteral)
    assert [it.value for it in result.ast.container.items] == [1, 2, 3]


def test_not_unary(evaluator):
    result = evaluator.validate("not verified")
    assert result.ok, result.error
    assert isinstance(result.ast, NotOp)
    assert isinstance(result.ast.operand, PathRef)
    assert result.ast.operand.dotted == "verified"


def test_and_chain(evaluator):
    result = evaluator.validate("a == 1 and b == 2")
    assert result.ok, result.error
    assert isinstance(result.ast, BoolOp)
    assert result.ast.op == "and"
    assert len(result.ast.operands) == 2
    assert all(isinstance(o, Compare) for o in result.ast.operands)


def test_or_nested_and(evaluator):
    result = evaluator.validate("a == 1 or (b == 2 and c == 3)")
    assert result.ok, result.error
    assert isinstance(result.ast, BoolOp)
    assert result.ast.op == "or"
    assert len(result.ast.operands) == 2
    # Second operand should be an AND BoolOp
    assert isinstance(result.ast.operands[1], BoolOp)
    assert result.ast.operands[1].op == "and"


def test_exists_function(evaluator):
    result = evaluator.validate("exists(borrower.income.amount)")
    assert result.ok, result.error
    assert isinstance(result.ast, FuncCall)
    assert result.ast.name == "exists"
    assert len(result.ast.args) == 1
    assert isinstance(result.ast.args[0], PathRef)
    assert result.ast.args[0].dotted == "borrower.income.amount"


def test_within_business_days_kwarg(evaluator):
    result = evaluator.validate(
        "within_business_days(3, anchor=application_received_at)"
    )
    assert result.ok, result.error
    assert isinstance(result.ast, FuncCall)
    assert result.ast.name == "within_business_days"
    assert len(result.ast.args) == 1
    assert isinstance(result.ast.args[0], Literal)
    assert result.ast.args[0].value == 3
    assert "anchor" in result.ast.kwargs
    anchor = result.ast.kwargs["anchor"]
    assert isinstance(anchor, PathRef)
    assert anchor.dotted == "application_received_at"


def test_matches_pattern(evaluator):
    result = evaluator.validate('matches_pattern(email, "^[a-z]+@")')
    assert result.ok, result.error
    assert isinstance(result.ast, FuncCall)
    assert result.ast.name == "matches_pattern"
    assert len(result.ast.args) == 2
    assert isinstance(result.ast.args[0], PathRef)
    assert result.ast.args[0].dotted == "email"
    assert isinstance(result.ast.args[1], Literal)
    assert result.ast.args[1].value == "^[a-z]+@"
    assert result.ast.args[1].type_hint == "string"


def test_is_empty(evaluator):
    result = evaluator.validate("is_empty(notes)")
    assert result.ok, result.error
    assert isinstance(result.ast, FuncCall)
    assert result.ast.name == "is_empty"
    assert len(result.ast.args) == 1
    assert isinstance(result.ast.args[0], PathRef)
    assert result.ast.args[0].dotted == "notes"


def test_or_range(evaluator):
    result = evaluator.validate("amount < 0 or amount > 1000000")
    assert result.ok, result.error
    assert isinstance(result.ast, BoolOp)
    assert result.ast.op == "or"
    assert len(result.ast.operands) == 2
    assert all(isinstance(o, Compare) for o in result.ast.operands)
    assert result.ast.operands[0].op == "<"
    assert result.ast.operands[1].op == ">"


def test_single_quoted_string(evaluator):
    result = evaluator.validate("employmentType == 'W2'")
    assert result.ok, result.error
    assert isinstance(result.ast, Compare)
    assert result.ast.op == "=="
    assert isinstance(result.ast.right, Literal)
    assert result.ast.right.value == "W2"
    assert result.ast.right.type_hint == "string"


def test_path_vs_path_compare(evaluator):
    result = evaluator.validate("variancePercent <= varianceThreshold")
    assert result.ok, result.error
    assert isinstance(result.ast, Compare)
    assert result.ast.op == "<="
    assert isinstance(result.ast.left, PathRef)
    assert result.ast.left.dotted == "variancePercent"
    assert isinstance(result.ast.right, PathRef)
    assert result.ast.right.dotted == "varianceThreshold"


def test_unknown_function_parses_fine(evaluator):
    # Phase 1 is parse-only: any function name is accepted syntactically.
    result = evaluator.validate("unknown_func(x)")
    assert result.ok, result.error
    assert isinstance(result.ast, FuncCall)
    assert result.ast.name == "unknown_func"


def test_between_function(evaluator):
    result = evaluator.validate("between(amount, 100, 500)")
    assert result.ok, result.error
    assert isinstance(result.ast, FuncCall)
    assert result.ast.name == "between"
    assert len(result.ast.args) == 3


def test_float_literal(evaluator):
    result = evaluator.validate("score >= 0.75")
    assert result.ok, result.error
    assert isinstance(result.ast, Compare)
    assert isinstance(result.ast.right, Literal)
    assert result.ast.right.value == 0.75
    assert result.ast.right.type_hint == "float"


# ---------------------------------------------------------------------------
# Invalid expressions
# ---------------------------------------------------------------------------
def test_empty_string(evaluator):
    result = evaluator.validate("")
    assert not result.ok
    assert result.error == "Empty expression"


def test_whitespace_only(evaluator):
    result = evaluator.validate("   \t\n ")
    assert not result.ok
    assert result.error == "Empty expression"


def test_dangling_operator(evaluator):
    result = evaluator.validate("a ==")
    assert not result.ok
    assert result.error


def test_unmatched_paren(evaluator):
    result = evaluator.validate("(a == 1")
    assert not result.ok
    assert result.error


def test_no_operator(evaluator):
    result = evaluator.validate("a b c")
    assert not result.ok
    assert result.error


def test_single_equals(evaluator):
    # `a = b` is not a valid comparison in our grammar.
    result = evaluator.validate("a = b")
    assert not result.ok
    assert result.error
