"""Expression parser for triple decision predicates.

Spec reference: files/04-static-handoff-checker.md §B4

Phase 1 scope: PARSE ONLY. Symbolic/concrete evaluation comes in Phase 2/3.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from lark import Lark, Transformer, UnexpectedInput, v_args

from triple_flow_sim.evaluator.ast_nodes import (
    BoolOp,
    Compare,
    ExprNode,
    FuncCall,
    InOp,
    ListLiteral,
    Literal,
    NotOp,
    PathRef,
)

GRAMMAR_PATH = Path(__file__).parent / "grammar.lark"


@dataclass
class ParseResult:
    """Structured result of ExpressionEvaluator.validate()."""
    ok: bool
    ast: Optional[ExprNode] = None
    error: Optional[str] = None
    error_line: Optional[int] = None
    error_column: Optional[int] = None


class _AstBuilder(Transformer):
    """Lark Transformer that builds typed AST nodes from the parse tree."""

    # ------------------------------------------------------------------
    # Entry
    # ------------------------------------------------------------------
    def start(self, items):
        return items[0]

    # ------------------------------------------------------------------
    # Boolean operators
    # ------------------------------------------------------------------
    def or_expr(self, items):
        # items interleaves operands and OR tokens; filter operands only.
        operands = [i for i in items if not _is_keyword_token(i, "or")]
        if len(operands) == 1:
            return operands[0]
        return BoolOp(op="or", operands=list(operands))

    def and_expr(self, items):
        operands = [i for i in items if not _is_keyword_token(i, "and")]
        if len(operands) == 1:
            return operands[0]
        return BoolOp(op="and", operands=list(operands))

    def not_op(self, items):
        # items = [NOT_token, operand]
        operand = items[-1]
        return NotOp(operand=operand)

    # ------------------------------------------------------------------
    # Comparison & membership
    # ------------------------------------------------------------------
    def compare(self, items):
        if len(items) == 1:
            return items[0]
        left, op_token, right = items
        return Compare(op=str(op_token), left=left, right=right)

    def in_op(self, items):
        # items may contain an IN token between member and container.
        nodes = [i for i in items if not _is_keyword_token(i, "in")]
        member, container = nodes[0], nodes[1]
        return InOp(member=member, container=container, negated=False)

    def not_in_op(self, items):
        nodes = [
            i for i in items
            if not _is_keyword_token(i, "not") and not _is_keyword_token(i, "in")
        ]
        member, container = nodes[0], nodes[1]
        return InOp(member=member, container=container, negated=True)

    # ------------------------------------------------------------------
    # Paths & literals
    # ------------------------------------------------------------------
    def path(self, items):
        segments = tuple(str(tok) for tok in items)
        return PathRef(segments=segments)

    def str_lit(self, items):
        raw = str(items[0])
        # Strip surrounding quotes (either ' or ")
        val = raw[1:-1]
        # Unescape common sequences
        val = val.replace('\\"', '"').replace("\\'", "'").replace("\\\\", "\\")
        return Literal(value=val, type_hint="string")

    def num_lit(self, items):
        s = str(items[0])
        if "." in s or "e" in s.lower():
            return Literal(value=float(s), type_hint="float")
        return Literal(value=int(s), type_hint="int")

    def true_lit(self, items):
        return Literal(value=True, type_hint="bool")

    def false_lit(self, items):
        return Literal(value=False, type_hint="bool")

    def null_lit(self, items):
        return Literal(value=None, type_hint="null")

    def literal(self, items):
        # Passthrough — individual typed rules (str_lit/num_lit/...) build the node.
        return items[0]

    def list_literal(self, items):
        return ListLiteral(items=list(items))

    # ------------------------------------------------------------------
    # Function calls
    # ------------------------------------------------------------------
    def func_call(self, items):
        name = str(items[0])
        positional: list[ExprNode] = []
        keywords: dict[str, ExprNode] = {}
        if len(items) > 1 and items[1] is not None:
            for arg in items[1]:
                if isinstance(arg, tuple) and len(arg) == 2 and isinstance(arg[0], str):
                    keywords[arg[0]] = arg[1]
                else:
                    positional.append(arg)
        return FuncCall(name=name, args=positional, kwargs=keywords)

    def args(self, items):
        return list(items)

    def kwarg(self, items):
        return (str(items[0]), items[1])

    def posarg(self, items):
        return items[0]


def _is_keyword_token(item, keyword: str) -> bool:
    """Return True if item is a Lark Token matching the given keyword text."""
    try:
        # Tokens have a .type attribute and str() returns their text.
        return hasattr(item, "type") and str(item) == keyword
    except Exception:
        return False


class ExpressionEvaluator:
    """Parser (and future evaluator) for predicate expressions.

    Phase 1: parse() / validate() only. Evaluation is a later phase.
    """

    def __init__(self):
        with open(GRAMMAR_PATH, "r", encoding="utf-8") as f:
            grammar = f.read()
        # Use Earley so the "not not_expr" alt with lookahead works cleanly.
        self._parser = Lark(grammar, parser="earley", start="start")
        self._builder = _AstBuilder()

    def parse(self, expr: str) -> ExprNode:
        """Parse an expression into an AST. Raises on syntax error."""
        if expr is None:
            raise ValueError("Cannot parse None")
        tree = self._parser.parse(expr)
        return self._builder.transform(tree)

    def validate(self, expr: str) -> ParseResult:
        """Parse and return a ParseResult. Never raises for syntax errors."""
        if expr is None or not expr.strip():
            return ParseResult(ok=False, error="Empty expression")
        try:
            ast = self.parse(expr)
            return ParseResult(ok=True, ast=ast)
        except UnexpectedInput as e:
            return ParseResult(
                ok=False,
                error=str(e),
                error_line=getattr(e, "line", None),
                error_column=getattr(e, "column", None),
            )
        except Exception as e:  # noqa: BLE001 — wrap any transformer/other failure
            return ParseResult(ok=False, error=f"Parse failed: {e}")
