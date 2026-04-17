"""StaticHandoffChecker facade.

Spec reference: files/04-static-handoff-checker.md §Public API
"""
from __future__ import annotations

from typing import Optional

import networkx as nx

from triple_flow_sim.contracts import BpmnNodeType, StateFieldRef, Triple
from triple_flow_sim.evaluator.parser import ExpressionEvaluator
from triple_flow_sim.evaluator.symbolic import SymbolicEvaluator

from triple_flow_sim.components.c04_static_handoff import pair_checks
from triple_flow_sim.components.c04_static_handoff import gateway_checks
from triple_flow_sim.components.c04_static_handoff.pair_enumeration import (
    enumerate_pairs,
)
from triple_flow_sim.components.c04_static_handoff.result import (
    GatewayCheckResult,
    PairCheckResult,
    StaticCheckReport,
)


class StaticHandoffChecker:
    """Facade that orchestrates C1-C6 and G1-G3 against a JourneyGraph."""

    def __init__(
        self,
        graph,
        evaluator: Optional[ExpressionEvaluator] = None,
        symbolic: Optional[SymbolicEvaluator] = None,
    ):
        self.graph = graph
        self.evaluator = evaluator or ExpressionEvaluator()
        self.symbolic = symbolic or SymbolicEvaluator()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def check_all(self) -> StaticCheckReport:
        report = StaticCheckReport()
        # Pair checks
        for producer_id, consumer_id, edge_id in enumerate_pairs(self.graph):
            result = self.check_pair(producer_id, consumer_id, edge_id)
            report.pair_results.append(result)
            report.pairs_checked += 1
        # Gateway checks
        for gw_id in self._gateway_ids():
            result = self.check_gateway(gw_id)
            report.gateway_results.append(result)
            report.gateways_checked += 1
        return report

    def check_pair(
        self,
        producer_id: str,
        consumer_id: str,
        edge_id: Optional[str] = None,
    ) -> PairCheckResult:
        producer = self.graph.get_triple(producer_id)
        consumer = self.graph.get_triple(consumer_id)
        result = PairCheckResult(
            producer_id=producer_id,
            consumer_id=consumer_id,
            edge_id=edge_id,
        )
        if producer is None or consumer is None:
            return result

        upstream_writes = self._upstream_writes(producer_id)
        downstream_closes = self._downstream_obligation_closes(consumer_id)

        result.detections.extend(
            pair_checks.c1_state_flow(
                producer, consumer, edge_id,
                self.evaluator, self.symbolic,
                upstream_writes=upstream_writes,
            )
        )
        result.detections.extend(
            pair_checks.c2_type_mismatch(
                producer, consumer, edge_id,
                self.evaluator, self.symbolic,
            )
        )
        result.detections.extend(
            pair_checks.c3_semantic(
                producer, consumer, edge_id,
                self.evaluator, self.symbolic,
            )
        )
        result.detections.extend(
            pair_checks.c4_obligations(
                producer, consumer, edge_id,
                self.evaluator, self.symbolic,
                downstream_closes=downstream_closes,
            )
        )
        result.detections.extend(
            pair_checks.c5_naming_drift(
                producer, consumer, edge_id,
                self.evaluator, self.symbolic,
            )
        )
        result.detections.extend(
            pair_checks.c6_implicit_setup(
                producer, consumer, edge_id,
                self.evaluator, self.symbolic,
                upstream_writes=upstream_writes,
            )
        )

        # De-duplicate: if both C1 and C2 flagged the same (signal_type, path)
        # for the same pair, keep one.
        result.detections = _dedupe(result.detections)
        result.verdict = "fail" if result.detections else "pass"
        return result

    def check_gateway(self, gateway_id: str) -> GatewayCheckResult:
        result = GatewayCheckResult(gateway_id=gateway_id)
        triple = self.graph.get_triple(gateway_id)
        if triple is None:
            return result
        result.detections.extend(gateway_checks.g1_evaluability(triple, self.evaluator))
        result.detections.extend(
            gateway_checks.g2_partitioning(triple, self.evaluator, self.symbolic)
        )
        result.detections.extend(gateway_checks.g3_coverage(triple))
        result.detections = _dedupe(result.detections)
        result.verdict = "fail" if result.detections else "pass"
        return result

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------
    def _gateway_ids(self) -> list[str]:
        nx_g = self.graph.networkx
        gws: list[str] = []
        for n, data in nx_g.nodes(data=True):
            if data.get("node_type") in (
                BpmnNodeType.EXCLUSIVE_GATEWAY,
                BpmnNodeType.PARALLEL_GATEWAY,
            ):
                if data.get("triple") is not None:
                    gws.append(n)
        return gws

    def _upstream_writes(self, node_id: str) -> dict[str, StateFieldRef]:
        """Aggregate state_writes from every ancestor of node_id (exclusive)."""
        writes: dict[str, StateFieldRef] = {}
        nx_g = self.graph.networkx
        if node_id not in nx_g.nodes:
            return writes
        try:
            ancestors = nx.ancestors(nx_g, node_id)
        except Exception:
            ancestors = set()
        for a in ancestors:
            triple = self.graph.get_triple(a)
            if triple is None or triple.pim is None:
                continue
            for sw in triple.pim.state_writes or []:
                writes.setdefault(sw.path, sw)
        return writes

    def _downstream_obligation_closes(self, node_id: str) -> set[str]:
        """Obligation IDs closed by any descendant of node_id (inclusive)."""
        closes: set[str] = set()
        nx_g = self.graph.networkx
        if node_id not in nx_g.nodes:
            return closes
        reachable: set[str] = {node_id}
        try:
            reachable |= nx.descendants(nx_g, node_id)
        except Exception:
            pass
        for n in reachable:
            triple = self.graph.get_triple(n)
            if triple is None or triple.pim is None:
                continue
            for ob_id in triple.pim.obligations_closed or []:
                closes.add(ob_id)
        return closes


def _dedupe(detections: list) -> list:
    seen: set[tuple] = set()
    out = []
    for d in detections:
        path = d.detector_context.get("path") if d.detector_context else None
        ob_id = (
            d.detector_context.get("obligation_id")
            if d.detector_context else None
        )
        edge_a = (
            d.detector_context.get("edge_a") if d.detector_context else None
        )
        key = (
            d.signal_type,
            d.primary_triple_id,
            tuple(d.related_triple_ids),
            d.bpmn_edge_id,
            path,
            ob_id,
            edge_a,
        )
        if key in seen:
            continue
        seen.add(key)
        out.append(d)
    return out
