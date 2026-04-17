"""Persona generator — canonical + boundary personas.

Spec reference: files/09-persona-generator.md.

Phase 3 scope: the canonical persona for a journey (baseline) plus two
boundary personas (edge cases that should still succeed). Full perturbation
is Phase 4 (Task 4.2).
"""
from triple_flow_sim.components.c06_persona.generator import (
    PersonaGenerator,
    build_canonical_persona,
    build_boundary_personas,
)

__all__ = [
    "PersonaGenerator",
    "build_canonical_persona",
    "build_boundary_personas",
]
