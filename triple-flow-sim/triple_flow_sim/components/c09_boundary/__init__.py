"""Branch boundary harness (component 08).

Spec reference: files/08-branch-boundary-harness.md.

For every exclusive gateway, generate state values that straddle the
branch predicates (just-above / just-below / exactly-on-boundary) and
observe whether the LLM consistently routes the way the declared predicate
demands. Divergence → ``branch_misdirection`` or ``predicate_non_partitioning``.

Phase 3 implementation uses the same fake LLM by default.
"""
from triple_flow_sim.components.c09_boundary.harness import (
    BranchBoundaryHarness,
    BoundaryProbeResult,
)

__all__ = ["BranchBoundaryHarness", "BoundaryProbeResult"]
