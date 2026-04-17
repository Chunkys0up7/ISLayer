"""Persona generator tests."""
from __future__ import annotations

from triple_flow_sim.components.c06_persona import (
    PersonaGenerator,
    build_boundary_personas,
    build_canonical_persona,
)
from triple_flow_sim.contracts import (
    AssertionPredicate,
    ContextAssertion,
    PIMLayer,
    StateFieldRef,
    Triple,
    TripleSet,
)


def _triple_with_reads(tid: str) -> Triple:
    return Triple(
        triple_id=tid,
        pim=PIMLayer(
            state_reads=[
                StateFieldRef(path="borrower.income", type="decimal"),
                StateFieldRef(path="borrower.name", type="string"),
            ]
        ),
    )


def _triple_with_range_precondition() -> Triple:
    return Triple(
        triple_id="T_range",
        pim=PIMLayer(
            preconditions=[
                ContextAssertion(
                    path="borrower.score",
                    predicate=AssertionPredicate.IN_RANGE,
                    value=[650, 850],
                    type="int",
                )
            ]
        ),
    )


def test_canonical_persona_populates_reads():
    ts = TripleSet(triples={"T1": _triple_with_reads("T1")})
    persona = build_canonical_persona(ts)
    assert "borrower" in persona.seed_state
    assert "income" in persona.seed_state["borrower"]
    assert "name" in persona.seed_state["borrower"]


def test_canonical_uses_precondition_values():
    ts = TripleSet(triples={"T_range": _triple_with_range_precondition()})
    persona = build_canonical_persona(ts)
    assert persona.seed_state["borrower"]["score"] == (650 + 850) / 2


def test_boundary_personas_generated():
    ts = TripleSet(triples={"T_range": _triple_with_range_precondition()})
    boundaries = build_boundary_personas(ts, limit=2)
    assert boundaries, "expected at least one boundary persona"
    assert boundaries[0].seed_state["borrower"]["score"] == 650


def test_generator_all_includes_canonical_plus_boundaries():
    ts = TripleSet(triples={"T_range": _triple_with_range_precondition()})
    personas = PersonaGenerator(ts).all(boundary_limit=1)
    assert personas[0].persona_id == "canonical"
    assert len(personas) >= 2
