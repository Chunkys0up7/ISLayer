"""Branch boundary harness implementation.

Spec reference: files/08-branch-boundary-harness.md §B1..B4.

The Phase 3 harness is a scaffold: it probes each gateway with three
synthetic states derived from the declared predicates and records which
branch the LLM picks. Divergence analysis is structural for now —
a full symbolic straddle generator arrives in Phase 4 alongside the
perturbation generator.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Optional

from triple_flow_sim.components.c05_llm import (
    FakeLLM,
    LLMClient,
    LLMRequest,
)
from triple_flow_sim.components.c05_llm.prompts import render
from triple_flow_sim.contracts import (
    BpmnNodeType,
    Evidence,
    Generator,
    RawDetection,
    Triple,
)


@dataclass
class BoundaryProbeResult:
    gateway_id: str
    triple_id: str
    probes: list[dict] = field(default_factory=list)  # per-probe outcomes
    branch_disagreements: list[dict] = field(default_factory=list)
    detections: list[RawDetection] = field(default_factory=list)


class BranchBoundaryHarness:
    """Probe each gateway with boundary-adjacent states."""

    def __init__(
        self,
        journey_graph,  # JourneyGraph
        llm: Optional[LLMClient] = None,
        seed: int = 0,
    ):
        self.graph = journey_graph
        self.llm = llm or FakeLLM(seed=seed)
        self.seed = seed

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def probe_all(self) -> list[BoundaryProbeResult]:
        results: list[BoundaryProbeResult] = []
        for node_id in self._exclusive_gateway_ids():
            triple = self.graph.get_triple(node_id)
            if triple is None:
                continue
            results.append(self.probe_gateway(node_id, triple))
        return results

    def probe_gateway(
        self, gateway_id: str, triple: Triple
    ) -> BoundaryProbeResult:
        result = BoundaryProbeResult(
            gateway_id=gateway_id, triple_id=triple.triple_id
        )
        predicates = (
            triple.pim.decision_predicates if triple.pim else None
        ) or []
        if not predicates:
            return result

        for bp in predicates:
            # Two probes: one where we claim the predicate is true, one where
            # we claim it is false. Phase 3 fake LLM will deterministically
            # echo; Phase 4 replaces this with symbolic-boundary generation.
            for flavor in ("true", "false"):
                probe_state = {
                    "predicate_expression": bp.predicate_expression,
                    "assumed_truth_value": flavor,
                }
                prompt = render(
                    "grounded_gateway",
                    triple_id=triple.triple_id,
                    intent=(triple.cim.intent if triple.cim else "") or "",
                    predicates=[
                        {
                            "edge_id": p.edge_id,
                            "expression": p.predicate_expression,
                            "is_default": p.is_default,
                        }
                        for p in predicates
                    ],
                    content_chunks=(
                        triple.psm.enriched_content if triple.psm else []
                    ) or [],
                    state_json=json.dumps(probe_state, sort_keys=True),
                )
                req = LLMRequest(
                    model=getattr(self.llm, "model", "fake"),
                    system=prompt.system,
                    prompt=prompt.prompt,
                    seed=self.seed,
                )
                resp = self.llm.complete(req)
                parsed = resp.parsed
                if parsed is None:
                    try:
                        parsed = json.loads(resp.raw_text)
                    except Exception:  # noqa: BLE001
                        parsed = {}
                chosen = (parsed or {}).get("edge_id")
                result.probes.append(
                    {
                        "edge_id": bp.edge_id,
                        "flavor": flavor,
                        "llm_choice": chosen,
                        "expression": bp.predicate_expression,
                    }
                )

        # Detect disagreements: two probes produced the same edge_id when
        # they were fed contradictory "assumed_truth_value" flavors.
        by_edge: dict[str, set[str]] = {}
        for p in result.probes:
            if p["llm_choice"] is not None:
                by_edge.setdefault(p["edge_id"], set()).add(
                    f"{p['flavor']}->{p['llm_choice']}"
                )
        for edge_id, responses in by_edge.items():
            if len(responses) == 1 and len(result.probes) > 1:
                # The LLM picked the same branch regardless of flavor.
                result.branch_disagreements.append(
                    {
                        "edge_id": edge_id,
                        "responses": sorted(responses),
                    }
                )
                result.detections.append(
                    RawDetection(
                        signal_type="branch_misdirection",
                        generator=Generator.BRANCH_BOUNDARY,
                        primary_triple_id=triple.triple_id,
                        bpmn_node_id=gateway_id,
                        bpmn_edge_id=edge_id,
                        detector_context={"responses": sorted(responses)},
                        evidence=Evidence(
                            observed=(
                                f"Gateway {gateway_id} chose edge {edge_id} "
                                f"under both true/false probe flavors."
                            )
                        ),
                    )
                )
        return result

    # ------------------------------------------------------------------
    def _exclusive_gateway_ids(self) -> list[str]:
        return [
            n
            for n, d in self.graph.networkx.nodes(data=True)
            if d.get("node_type") == BpmnNodeType.EXCLUSIVE_GATEWAY
        ]
