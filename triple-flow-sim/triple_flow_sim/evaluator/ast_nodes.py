"""Typed AST nodes for the expression evaluator.

Spec reference: files/04-static-handoff-checker.md §B4
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Union


@dataclass
class PathRef:
    """Dotted path reference, e.g. borrower.income.amount."""
    segments: tuple[str, ...]

    @property
    def dotted(self) -> str:
        return ".".join(self.segments)


@dataclass
class Literal:
    """A scalar literal (string, int, float, bool, or null)."""
    value: Any  # str, int, float, bool, None
    type_hint: str  # "string", "int", "float", "bool", "null"


@dataclass
class ListLiteral:
    """A list literal like [1, 2, 3] or ["a", "b"]."""
    items: list["ExprNode"]


@dataclass
class Compare:
    """A binary comparison: left OP right (==, !=, <, <=, >, >=)."""
    op: str
    left: "ExprNode"
    right: "ExprNode"


@dataclass
class BoolOp:
    """Boolean conjunction/disjunction over >=2 operands."""
    op: str  # "and" or "or"
    operands: list["ExprNode"]


@dataclass
class NotOp:
    """Logical negation."""
    operand: "ExprNode"


@dataclass
class InOp:
    """Membership test: member in container (or not in)."""
    member: "ExprNode"
    container: "ExprNode"
    negated: bool = False


@dataclass
class FuncCall:
    """Named function call with positional and/or keyword arguments.

    Canonical names: exists, within_business_days, matches_pattern,
    is_empty, between, length. Phase 1 accepts any function name.
    """
    name: str
    args: list["ExprNode"] = field(default_factory=list)
    kwargs: dict[str, "ExprNode"] = field(default_factory=dict)


ExprNode = Union[
    PathRef, Literal, ListLiteral, Compare, BoolOp, NotOp, InOp, FuncCall
]
