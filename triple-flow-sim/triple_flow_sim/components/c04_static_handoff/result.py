"""Dataclass contracts for StaticHandoffChecker results.

Spec reference: files/04-static-handoff-checker.md §B5, §B6
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from triple_flow_sim.contracts import RawDetection


@dataclass
class PairCheckResult:
    """Outcome of running C1-C6 against a single (producer, consumer) edge."""
    producer_id: str
    consumer_id: str
    edge_id: Optional[str] = None
    detections: list[RawDetection] = field(default_factory=list)
    verdict: str = "pass"  # pass | fail | partial


@dataclass
class GatewayCheckResult:
    """Outcome of running G1-G3 on a single gateway node."""
    gateway_id: str
    detections: list[RawDetection] = field(default_factory=list)
    verdict: str = "pass"


@dataclass
class StaticCheckReport:
    """Aggregate report produced by StaticHandoffChecker.check_all()."""
    pair_results: list[PairCheckResult] = field(default_factory=list)
    gateway_results: list[GatewayCheckResult] = field(default_factory=list)
    pairs_checked: int = 0
    gateways_checked: int = 0

    def all_detections(self) -> list[RawDetection]:
        out: list[RawDetection] = []
        for r in self.pair_results:
            out.extend(r.detections)
        for g in self.gateway_results:
            out.extend(g.detections)
        return out
