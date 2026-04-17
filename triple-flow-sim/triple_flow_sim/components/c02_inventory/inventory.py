"""TripleInventory facade. Spec: files/02-triple-inventory.md"""
from __future__ import annotations

from collections import Counter
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field

from triple_flow_sim.contracts import RawDetection, TripleSet
from triple_flow_sim.components.c02_inventory.completeness_matrix import build_matrix
from triple_flow_sim.components.c02_inventory.invariants import INVARIANTS
from triple_flow_sim.components.c02_inventory.naming_drift import detect_naming_drift


class ExclusionRecord(BaseModel):
    model_config = ConfigDict(extra="allow")

    triple_id: str
    reason: str  # "identity_incomplete" | "contract_missing"
    detail: str = ""


class InventoryReport(BaseModel):
    model_config = ConfigDict(extra="allow")

    corpus_version_hash: str = ""
    total_triples: int = 0
    completeness_matrix: dict = Field(default_factory=dict)
    raw_detections: list[RawDetection] = Field(default_factory=list)
    exclusions: list[ExclusionRecord] = Field(default_factory=list)
    stats: dict = Field(default_factory=dict)
    graph_warning: Optional[str] = None


class TripleInventory:
    """Runs all inventory invariants + graph detections + naming-drift.

    Usage:
        inv = TripleInventory(triple_set, graph=graph_or_None)
        report = inv.run()
        ready = inv.get_simulation_ready_set(report)
    """

    def __init__(self, triple_set: TripleSet, graph: Any = None):
        self.triple_set = triple_set
        self.graph = graph

    def run(self) -> InventoryReport:
        report = InventoryReport(
            corpus_version_hash=self.triple_set.corpus_version_hash,
            total_triples=len(self.triple_set),
        )
        report.completeness_matrix = build_matrix(self.triple_set)

        # Run all invariants.
        for invariant in INVARIANTS:
            detections = invariant.check(self.triple_set, self.graph)
            report.raw_detections.extend(detections)

        # Graph-level detections (orphan nodes) if graph provided.
        if self.graph is not None:
            try:
                report.raw_detections.extend(self.graph.detections)
            except AttributeError:
                # Tolerate alternative graph impls in tests.
                pass
        else:
            report.graph_warning = (
                "Graph not provided — invariants I6/I7 and orphan detection "
                "run in best-effort mode"
            )

        # Naming drift suspects.
        report.raw_detections.extend(detect_naming_drift(self.triple_set))

        # Exclusion list: I1 + I4 failures.
        excluded_ids: set[str] = set()
        for det in report.raw_detections:
            tid = det.primary_triple_id
            if not tid or tid == "<unnamed>":
                continue
            if det.signal_type == "missing_identity_field" and tid not in excluded_ids:
                excluded_ids.add(tid)
                report.exclusions.append(ExclusionRecord(
                    triple_id=tid,
                    reason="identity_incomplete",
                    detail=f"Missing: {det.detector_context.get('missing_fields')}",
                ))
            elif det.signal_type == "missing_contract_field" and tid not in excluded_ids:
                excluded_ids.add(tid)
                report.exclusions.append(ExclusionRecord(
                    triple_id=tid,
                    reason="contract_missing",
                    detail=f"Missing: {det.detector_context.get('field_name')}",
                ))

        # Stats
        signal_counts = Counter(d.signal_type for d in report.raw_detections)
        report.stats = {
            "detection_counts": dict(signal_counts),
            "total_detections": len(report.raw_detections),
            "excluded_triple_count": len(excluded_ids),
            "simulatable_triple_count": report.total_triples - len(excluded_ids),
        }
        return report

    def get_simulation_ready_set(self, report: InventoryReport) -> TripleSet:
        excluded = {e.triple_id for e in report.exclusions}
        ready = TripleSet(
            corpus_version_hash=self.triple_set.corpus_version_hash,
            triples={
                tid: t
                for tid, t in self.triple_set.triples.items()
                if tid not in excluded
            },
        )
        return ready
