"""Context Isolation Harness (component 07) — the keystone diagnostic.

Spec reference: files/07-context-isolation-harness.md.

Given a triple, runs the same input through the LLM at three escalating
levels of context deprivation:

  Level 1 — full declared content (happy path).
  Level 2 — declared-only state (no bonus content chunks).
  Level 3 — minimum viable prompt (no content, just goal and declared IO).

A triple that succeeds at Level 1 but degrades at Level 2 or 3 is riding on
context the contract does not guarantee. These are the most valuable
findings the simulator produces — they explain why production agents fail
when deployed into new toolchains where the implicit context is absent.
"""
from triple_flow_sim.components.c07_isolation.harness import (
    IsolationHarness,
    IsolationLevelResult,
    IsolationRunResult,
)

__all__ = [
    "IsolationHarness",
    "IsolationLevelResult",
    "IsolationRunResult",
]
