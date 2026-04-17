"""Content ablation generator.

Spec reference: files/10-perturbation-generator.md §Ablation.

Rather than changing the state, ablation removes content chunks from the
triple's PSM one at a time, then reruns. If the output changes when chunk C
is removed, C was load-bearing — and if C is not referenced in any
precondition or declared input, the step is relying on content the contract
does not guarantee. This complements the Context Isolation Harness.
"""
from __future__ import annotations

import copy
from dataclasses import dataclass, field
from typing import Optional

from triple_flow_sim.contracts import (
    Evidence,
    Generator,
    RawDetection,
    Triple,
)


@dataclass
class AblationSpec:
    chunk_id: str


@dataclass
class AblationOutcome:
    spec: AblationSpec
    baseline_response: dict
    ablated_response: dict
    diverged: bool = False
    detections: list[RawDetection] = field(default_factory=list)


def ablate_triple(triple: Triple, chunk_id: str) -> Triple:
    """Return a deep copy of ``triple`` with ``chunk_id`` removed from PSM."""
    t = copy.deepcopy(triple)
    if t.psm and t.psm.enriched_content:
        t.psm.enriched_content = [
            c for c in t.psm.enriched_content if c.chunk_id != chunk_id
        ]
    return t


class AblationGenerator:
    """Produce ablation specs + classify divergences."""

    def plan(self, triple: Triple) -> list[AblationSpec]:
        chunks = (triple.psm.enriched_content if triple.psm else None) or []
        return [AblationSpec(chunk_id=c.chunk_id) for c in chunks]

    def diff_to_detection(
        self, triple: Triple, outcome: AblationOutcome
    ) -> list[RawDetection]:
        if not outcome.diverged:
            return []
        return [
            RawDetection(
                signal_type="content_adjacent_not_actionable",
                generator=Generator.ABLATION,
                primary_triple_id=triple.triple_id,
                bpmn_node_id=triple.bpmn_node_id or None,
                detector_context={"chunk_id": outcome.spec.chunk_id},
                evidence=Evidence(
                    observed=(
                        f"Removing content chunk '{outcome.spec.chunk_id}' "
                        f"changed the response — load-bearing content not "
                        f"declared in the contract."
                    )
                ),
            )
        ]
