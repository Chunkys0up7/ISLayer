"""Grounded handoff runner (component 05/06 combined for Phase 3 scaffold).

Spec references:
- files/05-grounded-handoff-runner.md
- files/06-sequence-runner.md

Executes a triple against an LLM and mutates ``JourneyContext`` per the
declared contract. Phase 3 scaffold uses the fake driver by default.
"""
from triple_flow_sim.components.c08_grounded.runner import (
    GroundedRunner,
    SequenceRunner,
)

__all__ = ["GroundedRunner", "SequenceRunner"]
