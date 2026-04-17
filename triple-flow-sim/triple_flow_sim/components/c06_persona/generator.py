"""Persona generator.

Spec reference: files/09-persona-generator.md.

A persona wraps a named seed state that feeds the sequence runner. The
generator inspects each triple's ``pim.state_reads`` and ``preconditions`` to
build a minimally plausible state object — values chosen from type-driven
defaults. Boundary personas flip one boundary-predicate value at a time.

Phase 3 deliberately produces deterministic, type-based fillers rather than
faked-but-realistic data — Phase 4 adds the Faker integration.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

from triple_flow_sim.contracts import (
    AssertionPredicate,
    ContextAssertion,
    Persona,
    StateFieldRef,
    TripleSet,
)


# ---------------------------------------------------------------------------
# Defaults
# ---------------------------------------------------------------------------
_TYPE_DEFAULTS: dict[str, Any] = {
    "string": "x",
    "str": "x",
    "number": 0,
    "int": 0,
    "integer": 0,
    "decimal": 0.0,
    "float": 0.0,
    "bool": True,
    "boolean": True,
    "date": "2026-01-01",
    "datetime": "2026-01-01T00:00:00Z",
    "any": None,
    "array": [],
    "list": [],
    "object": {},
    "dict": {},
}


def _default_for_type(type_name: str) -> Any:
    return _TYPE_DEFAULTS.get(type_name.lower(), None)


def _set_path(state: dict, path: str, value: Any) -> None:
    """Set a dotted path into ``state``, creating intermediate dicts."""
    parts = path.split(".")
    cur = state
    for p in parts[:-1]:
        if p not in cur or not isinstance(cur[p], dict):
            cur[p] = {}
        cur = cur[p]
    cur[parts[-1]] = value


def _value_for_assertion(a: ContextAssertion) -> Any:
    """Best-effort value fulfilling the assertion predicate."""
    if a.predicate == AssertionPredicate.EQUALS and a.value is not None:
        return a.value
    if a.predicate == AssertionPredicate.IN_RANGE and isinstance(a.value, (list, tuple)):
        if len(a.value) >= 2:
            low, high = a.value[0], a.value[1]
            if isinstance(low, (int, float)) and isinstance(high, (int, float)):
                return (low + high) / 2
            return low
    if a.predicate == AssertionPredicate.MATCHES_PATTERN:
        return "pattern-ok"
    return _default_for_type(a.type or "any")


# ---------------------------------------------------------------------------
# Builders
# ---------------------------------------------------------------------------
def _seed_state_from_triples(triple_set: TripleSet) -> dict:
    state: dict = {}
    for triple in triple_set:
        pim = triple.pim
        if pim is None:
            continue
        if pim.state_reads:
            for ref in pim.state_reads:
                _set_path(state, ref.path, _default_for_type(ref.type))
        if pim.preconditions:
            for pc in pim.preconditions:
                _set_path(state, pc.path, _value_for_assertion(pc))
    return state


def build_canonical_persona(
    triple_set: TripleSet,
    persona_id: str = "canonical",
    description: str = "Canonical happy-path persona",
) -> Persona:
    """Build the baseline persona — every declared input gets a valid value."""
    return Persona(
        persona_id=persona_id,
        description=description,
        seed_state=_seed_state_from_triples(triple_set),
    )


def build_boundary_personas(
    triple_set: TripleSet, limit: int = 3
) -> list[Persona]:
    """Build up to ``limit`` boundary personas.

    Each persona flips exactly one in-range precondition to its lower bound,
    or one boolean to False, so boundary logic gets exercised. Deterministic
    ordering: iterate triples in triple_set order, preconditions in
    declaration order.
    """
    base_state = _seed_state_from_triples(triple_set)
    personas: list[Persona] = []

    for triple in triple_set:
        if len(personas) >= limit:
            break
        pim = triple.pim
        if pim is None or not pim.preconditions:
            continue
        for idx, pc in enumerate(pim.preconditions):
            if len(personas) >= limit:
                break
            # Deep-copy the baseline by JSON round-trip — good enough for
            # the canonical shape we produce here.
            import copy

            variant = copy.deepcopy(base_state)
            if pc.predicate == AssertionPredicate.IN_RANGE and isinstance(
                pc.value, (list, tuple)
            ) and len(pc.value) >= 2:
                low = pc.value[0]
                _set_path(variant, pc.path, low)
                kind = "range_lower_bound"
            elif pc.predicate == AssertionPredicate.EQUALS:
                kind = "equals_flip"
                flip = pc.value if pc.value is None else not bool(pc.value)
                _set_path(variant, pc.path, flip)
            elif (pc.type or "").lower() in {"bool", "boolean"}:
                kind = "boolean_flip"
                _set_path(variant, pc.path, False)
            else:
                continue
            personas.append(
                Persona(
                    persona_id=f"boundary-{triple.triple_id}-{idx}-{kind}",
                    description=(
                        f"Boundary persona: {kind} on "
                        f"{triple.triple_id}.{pc.path}"
                    ),
                    seed_state=variant,
                )
            )
    return personas


# ---------------------------------------------------------------------------
# Facade
# ---------------------------------------------------------------------------
@dataclass
class PersonaGenerator:
    triple_set: TripleSet

    def canonical(self) -> Persona:
        return build_canonical_persona(self.triple_set)

    def boundaries(self, limit: int = 3) -> list[Persona]:
        return build_boundary_personas(self.triple_set, limit=limit)

    def all(self, boundary_limit: int = 3) -> list[Persona]:
        return [self.canonical()] + self.boundaries(boundary_limit)
