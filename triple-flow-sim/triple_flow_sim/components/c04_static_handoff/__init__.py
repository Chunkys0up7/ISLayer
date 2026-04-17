"""Component 04 — Static Handoff Checker.

Spec reference: files/04-static-handoff-checker.md

Public exports:
    StaticHandoffChecker (facade)
    StaticCheckReport, PairCheckResult, GatewayCheckResult
"""
from triple_flow_sim.components.c04_static_handoff.checker import (
    StaticHandoffChecker,
)
from triple_flow_sim.components.c04_static_handoff.result import (
    GatewayCheckResult,
    PairCheckResult,
    StaticCheckReport,
)

__all__ = [
    "StaticHandoffChecker",
    "StaticCheckReport",
    "PairCheckResult",
    "GatewayCheckResult",
]
