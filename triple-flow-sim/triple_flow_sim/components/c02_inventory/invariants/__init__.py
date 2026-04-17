"""Inventory invariants I1-I10.

Each submodule exposes `check(triple_set, graph=None) -> list[RawDetection]`.
"""
from . import (
    i01_identity,
    i02_layer,
    i03_intent,
    i04_contract,
    i05_gateway_predicates,
    i06_obligation_closure,
    i07_state_flow,
    i08_content_presence,
    i09_predicate_evaluability,
    i10_regulatory_resolution,
)

INVARIANTS = [
    i01_identity,
    i02_layer,
    i03_intent,
    i04_contract,
    i05_gateway_predicates,
    i06_obligation_closure,
    i07_state_flow,
    i08_content_presence,
    i09_predicate_evaluability,
    i10_regulatory_resolution,
]

__all__ = ["INVARIANTS"]
