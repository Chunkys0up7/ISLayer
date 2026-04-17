"""Symbolic evaluation for predicate expressions.

Compares a producer's postcondition against a consumer's precondition and
produces a conservative verdict: ALWAYS_SATISFIED, NEVER_SATISFIED,
SOMETIMES_SATISFIED, or UNDETERMINED.

Spec reference: files/04-static-handoff-checker.md §B4 (symbolic mode) and
§B2/C3 (predicate satisfiability for pair checks).

Design principle (per spec §B4 "Implementation notes"):
    When in doubt, return UNDETERMINED rather than risk a false positive.

Phase 2 scope: structural/symbolic comparison of ContextAssertions and of
simple parsed predicate ASTs. No concrete state substitution here — that
comes in Phase 3.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Iterable, Optional

from .ast_nodes import (
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


# ---------------------------------------------------------------------------
# Public result types
# ---------------------------------------------------------------------------
class SymbolicVerdict(str, Enum):
    """Conservative outcome of a producer-vs-consumer symbolic comparison."""

    ALWAYS_SATISFIED = "always_satisfied"
    NEVER_SATISFIED = "never_satisfied"
    SOMETIMES_SATISFIED = "sometimes_satisfied"
    UNDETERMINED = "undetermined"


@dataclass
class SymbolicResult:
    """Structured result of a symbolic comparison."""

    verdict: SymbolicVerdict
    reason: str = ""
    contradictions: list[str] = field(default_factory=list)
    gaps: list[str] = field(default_factory=list)
    overlaps: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Verdict combinators
# ---------------------------------------------------------------------------
# Strictness ordering used for compound AND:
#     NEVER > SOMETIMES > UNDETERMINED > ALWAYS
# (i.e. the worst/most-restrictive verdict wins).
_AND_STRICTNESS = {
    SymbolicVerdict.NEVER_SATISFIED: 3,
    SymbolicVerdict.SOMETIMES_SATISFIED: 2,
    SymbolicVerdict.UNDETERMINED: 1,
    SymbolicVerdict.ALWAYS_SATISFIED: 0,
}


def _combine_and(verdicts: list[SymbolicVerdict]) -> SymbolicVerdict:
    """AND combinator.

    Tie-breaking rule: the worst (most restrictive) clause dominates. Any NEVER
    makes the whole thing NEVER. Any SOMETIMES (and no NEVER) makes it
    SOMETIMES. Otherwise, any UNDETERMINED makes it UNDETERMINED. Only when
    every clause is ALWAYS does the conjunction resolve to ALWAYS.

    Rationale: AND requires every clause to hold. If any clause is known to
    fail, the conjunction fails. Conservatively, UNDETERMINED beats ALWAYS
    because we can't promise the unknown clause holds; SOMETIMES beats
    UNDETERMINED because we already have positive evidence of a gap.
    """
    if not verdicts:
        return SymbolicVerdict.UNDETERMINED
    worst = max(verdicts, key=lambda v: _AND_STRICTNESS[v])
    return worst


def _combine_or(verdicts: list[SymbolicVerdict]) -> SymbolicVerdict:
    """OR combinator.

    If any branch is ALWAYS → ALWAYS (OR is satisfied regardless of others).
    If all branches are NEVER → NEVER.
    Otherwise SOMETIMES if any branch is SOMETIMES, else UNDETERMINED.
    """
    if not verdicts:
        return SymbolicVerdict.UNDETERMINED
    if any(v == SymbolicVerdict.ALWAYS_SATISFIED for v in verdicts):
        return SymbolicVerdict.ALWAYS_SATISFIED
    if all(v == SymbolicVerdict.NEVER_SATISFIED for v in verdicts):
        return SymbolicVerdict.NEVER_SATISFIED
    if any(v == SymbolicVerdict.SOMETIMES_SATISFIED for v in verdicts):
        return SymbolicVerdict.SOMETIMES_SATISFIED
    return SymbolicVerdict.UNDETERMINED


def _negate(verdict: SymbolicVerdict) -> SymbolicVerdict:
    """Swap ALWAYS <-> NEVER, leave SOMETIMES/UNDETERMINED unchanged."""
    if verdict == SymbolicVerdict.ALWAYS_SATISFIED:
        return SymbolicVerdict.NEVER_SATISFIED
    if verdict == SymbolicVerdict.NEVER_SATISFIED:
        return SymbolicVerdict.ALWAYS_SATISFIED
    return verdict


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _iter_paths(node: ExprNode) -> Iterable[str]:
    """Yield every dotted path referenced inside an AST (may include dups)."""
    if isinstance(node, PathRef):
        yield node.dotted
    elif isinstance(node, Compare):
        yield from _iter_paths(node.left)
        yield from _iter_paths(node.right)
    elif isinstance(node, BoolOp):
        for op in node.operands:
            yield from _iter_paths(op)
    elif isinstance(node, NotOp):
        yield from _iter_paths(node.operand)
    elif isinstance(node, InOp):
        yield from _iter_paths(node.member)
        yield from _iter_paths(node.container)
    elif isinstance(node, FuncCall):
        for arg in node.args:
            yield from _iter_paths(arg)
        for arg in node.kwargs.values():
            yield from _iter_paths(arg)
    elif isinstance(node, ListLiteral):
        for item in node.items:
            yield from _iter_paths(item)


def _literal_value(node: ExprNode) -> tuple[bool, Any]:
    """Return (is_literal, value) for a node."""
    if isinstance(node, Literal):
        return True, node.value
    return False, None


def _as_path(node: ExprNode) -> Optional[str]:
    if isinstance(node, PathRef):
        return node.dotted
    return None


def _exists_arg(node: ExprNode) -> Optional[str]:
    """If node is exists(path) return the dotted path, else None."""
    if isinstance(node, FuncCall) and node.name.lower() == "exists" and node.args:
        return _as_path(node.args[0])
    return None


def _is_empty_arg(node: ExprNode) -> Optional[str]:
    if isinstance(node, FuncCall) and node.name.lower() == "is_empty" and node.args:
        return _as_path(node.args[0])
    return None


def _walk(node: ExprNode) -> Iterable[ExprNode]:
    """Pre-order walk yielding every AST node."""
    yield node
    if isinstance(node, BoolOp):
        for op in node.operands:
            yield from _walk(op)
    elif isinstance(node, NotOp):
        yield from _walk(node.operand)
    elif isinstance(node, Compare):
        yield from _walk(node.left)
        yield from _walk(node.right)
    elif isinstance(node, InOp):
        yield from _walk(node.member)
        yield from _walk(node.container)
    elif isinstance(node, FuncCall):
        for arg in node.args:
            yield from _walk(arg)
        for arg in node.kwargs.values():
            yield from _walk(arg)
    elif isinstance(node, ListLiteral):
        for item in node.items:
            yield from _walk(item)


def _in_range_call(node: ExprNode) -> Optional[tuple[str, Any, Any]]:
    """Extract (path, lo, hi) from an in_range(path, lo, hi) FuncCall.

    Returns None if the node doesn't fit that shape.
    """
    if not isinstance(node, FuncCall):
        return None
    if node.name.lower() != "in_range":
        return None
    args = list(node.args)
    if len(args) >= 3:
        path = _as_path(args[0])
        lo_is_lit, lo_val = _literal_value(args[1])
        hi_is_lit, hi_val = _literal_value(args[2])
        if path is not None and lo_is_lit and hi_is_lit:
            return path, lo_val, hi_val
    return None


def _range_bounds(value: Any) -> tuple[Any, Any]:
    """Pull (lo, hi) out of an IN_RANGE ContextAssertion.value.

    Accepts list/tuple of 2 or dict with 'min'/'max' (also 'low'/'high').
    """
    if isinstance(value, (list, tuple)) and len(value) == 2:
        return value[0], value[1]
    if isinstance(value, dict):
        lo = value.get("min", value.get("low"))
        hi = value.get("max", value.get("high"))
        if lo is not None and hi is not None:
            return lo, hi
    return None, None


# ---------------------------------------------------------------------------
# SymbolicEvaluator
# ---------------------------------------------------------------------------
class SymbolicEvaluator:
    """Conservatively compare producer and consumer predicates.

    Two entry points:

    * ``compare(producer_expr, consumer_expr)`` — compare parsed ASTs of
      expression strings. Handles boolean compound expressions, negation,
      equality with literals, exists(), is_empty(), and in_range().

    * ``compare_assertions(producer_assertions, consumer_assertions)`` —
      lists of ContextAssertion objects. For each consumer assertion we look
      up matching producer assertions by path and apply per-predicate rules.
    """

    # -----------------------------------------------------------------
    # AST-level compare
    # -----------------------------------------------------------------
    def compare(
        self, producer_expr: ExprNode, consumer_expr: ExprNode
    ) -> SymbolicResult:
        return self._compare_ast(producer_expr, consumer_expr)

    def _compare_ast(
        self, producer: ExprNode, consumer: ExprNode
    ) -> SymbolicResult:
        # Decompose consumer boolean structure first.
        if isinstance(consumer, BoolOp) and consumer.op == "and":
            sub = [self._compare_ast(producer, op) for op in consumer.operands]
            verdict = _combine_and([r.verdict for r in sub])
            return self._merge_results(verdict, sub, "consumer AND")
        if isinstance(consumer, BoolOp) and consumer.op == "or":
            sub = [self._compare_ast(producer, op) for op in consumer.operands]
            verdict = _combine_or([r.verdict for r in sub])
            return self._merge_results(verdict, sub, "consumer OR")
        if isinstance(consumer, NotOp):
            inner = self._compare_ast(producer, consumer.operand)
            return SymbolicResult(
                verdict=_negate(inner.verdict),
                reason=f"negated: {inner.reason}",
                contradictions=list(inner.contradictions),
                gaps=list(inner.gaps),
                overlaps=list(inner.overlaps),
            )

        # Producer AND: any ALWAYS/NEVER clause carries; we prefer the
        # strongest clause.
        if isinstance(producer, BoolOp) and producer.op == "and":
            sub = [self._compare_ast(op, consumer) for op in producer.operands]
            verdicts = [r.verdict for r in sub]
            if SymbolicVerdict.NEVER_SATISFIED in verdicts:
                return next(
                    r for r in sub if r.verdict == SymbolicVerdict.NEVER_SATISFIED
                )
            if SymbolicVerdict.ALWAYS_SATISFIED in verdicts:
                return next(
                    r for r in sub if r.verdict == SymbolicVerdict.ALWAYS_SATISFIED
                )
            if SymbolicVerdict.SOMETIMES_SATISFIED in verdicts:
                return next(
                    r
                    for r in sub
                    if r.verdict == SymbolicVerdict.SOMETIMES_SATISFIED
                )
            return sub[0]

        # Atomic consumer against (possibly atomic) producer.
        return self._compare_atomic(producer, consumer)

    # -----------------------------------------------------------------
    # Atomic comparison
    # -----------------------------------------------------------------
    def _compare_atomic(
        self, producer: ExprNode, consumer: ExprNode
    ) -> SymbolicResult:
        cons_exists_path = _exists_arg(consumer)
        if cons_exists_path is not None:
            return self._check_exists(producer, cons_exists_path)

        cons_empty_path = _is_empty_arg(consumer)
        if cons_empty_path is not None:
            res = self._check_exists(producer, cons_empty_path)
            return SymbolicResult(
                verdict=_negate(res.verdict),
                reason=f"is_empty: {res.reason}",
                contradictions=list(res.contradictions),
                gaps=list(res.gaps),
                overlaps=list(res.overlaps),
            )

        cons_range = _in_range_call(consumer)
        if cons_range is not None:
            path, lo, hi = cons_range
            return self._check_in_range(producer, path, lo, hi)

        if isinstance(consumer, Compare):
            return self._check_compare(producer, consumer)

        paths = sorted(set(_iter_paths(consumer)))
        return SymbolicResult(
            verdict=SymbolicVerdict.UNDETERMINED,
            reason="consumer predicate not in a symbolically-decidable form",
            gaps=[f"unanalyzable: {p}" for p in paths] if paths else [],
        )

    # -----------------------------------------------------------------
    # Rule: exists
    # -----------------------------------------------------------------
    def _check_exists(self, producer: ExprNode, path: str) -> SymbolicResult:
        for node in _walk(producer):
            if _exists_arg(node) == path:
                return SymbolicResult(
                    verdict=SymbolicVerdict.ALWAYS_SATISFIED,
                    reason=f"producer asserts exists({path})",
                    overlaps=[path],
                )
            if _is_empty_arg(node) == path:
                return SymbolicResult(
                    verdict=SymbolicVerdict.NEVER_SATISFIED,
                    reason=f"producer asserts is_empty({path}), contradicts exists",
                    contradictions=[path],
                )
        if path in set(_iter_paths(producer)):
            return SymbolicResult(
                verdict=SymbolicVerdict.ALWAYS_SATISFIED,
                reason=f"producer references {path} in an assertion",
                overlaps=[path],
            )
        return SymbolicResult(
            verdict=SymbolicVerdict.UNDETERMINED,
            reason=f"producer does not mention {path}",
            gaps=[path],
        )

    # -----------------------------------------------------------------
    # Rule: compare (path OP literal)
    # -----------------------------------------------------------------
    def _check_compare(
        self, producer: ExprNode, consumer: Compare
    ) -> SymbolicResult:
        path = _as_path(consumer.left)
        is_lit, lit = _literal_value(consumer.right)
        if path is None or not is_lit:
            alt_path = _as_path(consumer.right)
            alt_is_lit, alt_lit = _literal_value(consumer.left)
            if alt_path is not None and alt_is_lit:
                path, lit, is_lit = alt_path, alt_lit, True
        if path is None or not is_lit:
            return SymbolicResult(
                verdict=SymbolicVerdict.UNDETERMINED,
                reason="compare not of form path OP literal",
            )

        op = consumer.op
        for node in _walk(producer):
            if isinstance(node, Compare):
                p_path = _as_path(node.left)
                p_is_lit, p_lit = _literal_value(node.right)
                if p_path != path:
                    alt_p_path = _as_path(node.right)
                    alt_p_is_lit, alt_p_lit = _literal_value(node.left)
                    if alt_p_path == path and alt_p_is_lit:
                        p_path, p_lit, p_is_lit = alt_p_path, alt_p_lit, True
                if p_path == path and p_is_lit and node.op == op == "==":
                    if p_lit == lit:
                        return SymbolicResult(
                            verdict=SymbolicVerdict.ALWAYS_SATISFIED,
                            reason=f"producer asserts {path} == {lit!r}",
                            overlaps=[path],
                        )
                    return SymbolicResult(
                        verdict=SymbolicVerdict.NEVER_SATISFIED,
                        reason=(
                            f"producer asserts {path} == {p_lit!r}, "
                            f"consumer requires {lit!r}"
                        ),
                        contradictions=[path],
                    )
        if path not in set(_iter_paths(producer)):
            return SymbolicResult(
                verdict=SymbolicVerdict.UNDETERMINED,
                reason=f"producer does not constrain {path}",
                gaps=[path],
            )
        return SymbolicResult(
            verdict=SymbolicVerdict.UNDETERMINED,
            reason=f"producer mentions {path} but not in a comparable form",
            gaps=[path],
        )

    # -----------------------------------------------------------------
    # Rule: in_range
    # -----------------------------------------------------------------
    def _check_in_range(
        self, producer: ExprNode, path: str, lo: Any, hi: Any
    ) -> SymbolicResult:
        for node in _walk(producer):
            p_range = _in_range_call(node)
            if p_range is not None and p_range[0] == path:
                _, p_lo, p_hi = p_range
                return self._range_verdict(path, p_lo, p_hi, lo, hi)
        if path not in set(_iter_paths(producer)):
            return SymbolicResult(
                verdict=SymbolicVerdict.UNDETERMINED,
                reason=f"producer does not constrain {path} range",
                gaps=[path],
            )
        return SymbolicResult(
            verdict=SymbolicVerdict.UNDETERMINED,
            reason=f"producer references {path} but no in_range found",
            gaps=[path],
        )

    def _range_verdict(
        self, path: str, p_lo: Any, p_hi: Any, c_lo: Any, c_hi: Any
    ) -> SymbolicResult:
        try:
            if p_lo >= c_lo and p_hi <= c_hi:
                return SymbolicResult(
                    verdict=SymbolicVerdict.ALWAYS_SATISFIED,
                    reason=(
                        f"producer range [{p_lo},{p_hi}] subset of "
                        f"consumer [{c_lo},{c_hi}]"
                    ),
                    overlaps=[path],
                )
            if p_hi < c_lo or p_lo > c_hi:
                return SymbolicResult(
                    verdict=SymbolicVerdict.NEVER_SATISFIED,
                    reason=(
                        f"producer range [{p_lo},{p_hi}] disjoint from "
                        f"consumer [{c_lo},{c_hi}]"
                    ),
                    contradictions=[path],
                )
            return SymbolicResult(
                verdict=SymbolicVerdict.SOMETIMES_SATISFIED,
                reason=(
                    f"producer range [{p_lo},{p_hi}] overlaps but not "
                    f"contained in consumer [{c_lo},{c_hi}]"
                ),
                overlaps=[path],
            )
        except TypeError:
            return SymbolicResult(
                verdict=SymbolicVerdict.UNDETERMINED,
                reason=f"range bounds not comparable for {path}",
                gaps=[path],
            )

    # -----------------------------------------------------------------
    # Merge helper
    # -----------------------------------------------------------------
    def _merge_results(
        self,
        verdict: SymbolicVerdict,
        sub: list[SymbolicResult],
        label: str,
    ) -> SymbolicResult:
        gaps: list[str] = []
        overlaps: list[str] = []
        contradictions: list[str] = []
        reasons: list[str] = []
        for r in sub:
            gaps.extend(r.gaps)
            overlaps.extend(r.overlaps)
            contradictions.extend(r.contradictions)
            if r.reason:
                reasons.append(r.reason)
        reason = f"{label}: " + "; ".join(reasons) if reasons else label
        return SymbolicResult(
            verdict=verdict,
            reason=reason,
            contradictions=contradictions,
            gaps=gaps,
            overlaps=overlaps,
        )

    # -----------------------------------------------------------------
    # Assertion-list compare
    # -----------------------------------------------------------------
    def compare_assertions(
        self,
        producer_assertions: list,
        consumer_assertions: list,
    ) -> SymbolicResult:
        """Compare two lists of ContextAssertion objects.

        For each consumer assertion we evaluate its per-predicate verdict
        against the full set of producer assertions (plus any parsed
        SATISFIES_EXPRESSION strings), then AND the per-clause verdicts.
        """
        if not consumer_assertions:
            return SymbolicResult(
                verdict=SymbolicVerdict.ALWAYS_SATISFIED,
                reason="consumer has no preconditions",
            )

        # Late imports to avoid coupling at module import time.
        from triple_flow_sim.contracts.triple import AssertionPredicate
        from .parser import ExpressionEvaluator

        parser = ExpressionEvaluator()
        producer_exprs: list[ExprNode] = []
        for a in producer_assertions:
            if a.predicate == AssertionPredicate.SATISFIES_EXPRESSION and isinstance(
                a.value, str
            ):
                try:
                    producer_exprs.append(parser.parse(a.value))
                except Exception:  # noqa: BLE001
                    pass  # unparseable producer expressions are ignored

        per_clause: list[SymbolicResult] = []
        for c in consumer_assertions:
            per_clause.append(
                self._check_assertion(c, producer_assertions, producer_exprs, parser)
            )

        verdict = _combine_and([r.verdict for r in per_clause])
        return self._merge_results(verdict, per_clause, "assertions AND")

    def _check_assertion(
        self,
        consumer,  # ContextAssertion
        producer_assertions: list,
        producer_exprs: list[ExprNode],
        parser,
    ) -> SymbolicResult:
        from triple_flow_sim.contracts.triple import AssertionPredicate

        path = consumer.path
        matching = [a for a in producer_assertions if a.path == path]

        if consumer.predicate == AssertionPredicate.EXISTS:
            return self._assertion_exists(path, matching, producer_exprs)

        if consumer.predicate == AssertionPredicate.EQUALS:
            return self._assertion_equals(path, consumer.value, matching)

        if consumer.predicate == AssertionPredicate.IN_RANGE:
            return self._assertion_range(path, consumer.value, matching)

        if consumer.predicate == AssertionPredicate.MATCHES_PATTERN:
            return self._assertion_pattern(path, consumer.value, matching)

        if consumer.predicate == AssertionPredicate.SATISFIES_EXPRESSION:
            if not isinstance(consumer.value, str):
                return SymbolicResult(
                    verdict=SymbolicVerdict.UNDETERMINED,
                    reason="SATISFIES_EXPRESSION value is not a string",
                )
            try:
                cons_ast = parser.parse(consumer.value)
            except Exception as e:  # noqa: BLE001
                return SymbolicResult(
                    verdict=SymbolicVerdict.UNDETERMINED,
                    reason=f"consumer expression did not parse: {e}",
                )
            if not producer_exprs:
                return SymbolicResult(
                    verdict=SymbolicVerdict.UNDETERMINED,
                    reason="producer has no parseable expressions",
                    gaps=sorted(set(_iter_paths(cons_ast))),
                )
            if len(producer_exprs) == 1:
                prod_ast = producer_exprs[0]
            else:
                prod_ast = BoolOp(op="and", operands=list(producer_exprs))
            return self._compare_ast(prod_ast, cons_ast)

        return SymbolicResult(
            verdict=SymbolicVerdict.UNDETERMINED,
            reason=f"unknown predicate {consumer.predicate!r}",
        )

    # ----- per-predicate assertion helpers -----
    def _assertion_exists(
        self, path: str, matching: list, producer_exprs: list[ExprNode]
    ) -> SymbolicResult:
        from triple_flow_sim.contracts.triple import AssertionPredicate

        if matching:
            # Any matching assertion means producer constrains this path.
            # (SATISFIES_EXPRESSION could encode is_empty, but matching by
            # path alone is enough evidence of presence.)
            return SymbolicResult(
                verdict=SymbolicVerdict.ALWAYS_SATISFIED,
                reason=f"producer asserts {path}",
                overlaps=[path],
            )
        for expr in producer_exprs:
            for node in _walk(expr):
                if _is_empty_arg(node) == path:
                    return SymbolicResult(
                        verdict=SymbolicVerdict.NEVER_SATISFIED,
                        reason=f"producer asserts is_empty({path})",
                        contradictions=[path],
                    )
            if path in set(_iter_paths(expr)):
                return SymbolicResult(
                    verdict=SymbolicVerdict.ALWAYS_SATISFIED,
                    reason=f"producer expression references {path}",
                    overlaps=[path],
                )
        return SymbolicResult(
            verdict=SymbolicVerdict.UNDETERMINED,
            reason=f"producer does not mention {path}",
            gaps=[path],
        )

    def _assertion_equals(
        self, path: str, value: Any, matching: list
    ) -> SymbolicResult:
        from triple_flow_sim.contracts.triple import AssertionPredicate

        for a in matching:
            if a.predicate == AssertionPredicate.EQUALS:
                if a.value == value:
                    return SymbolicResult(
                        verdict=SymbolicVerdict.ALWAYS_SATISFIED,
                        reason=f"producer asserts {path} == {value!r}",
                        overlaps=[path],
                    )
                return SymbolicResult(
                    verdict=SymbolicVerdict.NEVER_SATISFIED,
                    reason=(
                        f"producer asserts {path} == {a.value!r}, "
                        f"consumer requires {value!r}"
                    ),
                    contradictions=[path],
                )
        if matching:
            return SymbolicResult(
                verdict=SymbolicVerdict.UNDETERMINED,
                reason=f"producer asserts {path} but not via EQUALS",
                gaps=[path],
            )
        return SymbolicResult(
            verdict=SymbolicVerdict.UNDETERMINED,
            reason=f"producer does not constrain {path}",
            gaps=[path],
        )

    def _assertion_range(
        self, path: str, value: Any, matching: list
    ) -> SymbolicResult:
        from triple_flow_sim.contracts.triple import AssertionPredicate

        c_lo, c_hi = _range_bounds(value)
        if c_lo is None or c_hi is None:
            return SymbolicResult(
                verdict=SymbolicVerdict.UNDETERMINED,
                reason=f"consumer IN_RANGE value not a [lo, hi] pair for {path}",
                gaps=[path],
            )
        for a in matching:
            if a.predicate == AssertionPredicate.IN_RANGE:
                p_lo, p_hi = _range_bounds(a.value)
                if p_lo is None or p_hi is None:
                    continue
                return self._range_verdict(path, p_lo, p_hi, c_lo, c_hi)
            if a.predicate == AssertionPredicate.EQUALS:
                try:
                    if c_lo <= a.value <= c_hi:
                        return SymbolicResult(
                            verdict=SymbolicVerdict.ALWAYS_SATISFIED,
                            reason=(
                                f"producer asserts {path} == {a.value!r} "
                                f"within [{c_lo},{c_hi}]"
                            ),
                            overlaps=[path],
                        )
                    return SymbolicResult(
                        verdict=SymbolicVerdict.NEVER_SATISFIED,
                        reason=(
                            f"producer asserts {path} == {a.value!r} "
                            f"outside [{c_lo},{c_hi}]"
                        ),
                        contradictions=[path],
                    )
                except TypeError:
                    pass
        return SymbolicResult(
            verdict=SymbolicVerdict.UNDETERMINED,
            reason=f"producer does not constrain range of {path}",
            gaps=[path],
        )

    def _assertion_pattern(
        self, path: str, value: Any, matching: list
    ) -> SymbolicResult:
        from triple_flow_sim.contracts.triple import AssertionPredicate

        for a in matching:
            if a.predicate == AssertionPredicate.MATCHES_PATTERN:
                if a.value == value:
                    return SymbolicResult(
                        verdict=SymbolicVerdict.ALWAYS_SATISFIED,
                        reason=f"producer and consumer share pattern for {path}",
                        overlaps=[path],
                    )
                # Language containment of arbitrary regexes is undecidable
                # in general — stay conservative.
                return SymbolicResult(
                    verdict=SymbolicVerdict.UNDETERMINED,
                    reason=(
                        f"producer pattern {a.value!r} vs consumer {value!r} "
                        f"not proven equivalent for {path}"
                    ),
                    gaps=[path],
                )
        return SymbolicResult(
            verdict=SymbolicVerdict.UNDETERMINED,
            reason=f"producer does not constrain pattern of {path}",
            gaps=[path],
        )


__all__ = [
    "SymbolicVerdict",
    "SymbolicResult",
    "SymbolicEvaluator",
]
