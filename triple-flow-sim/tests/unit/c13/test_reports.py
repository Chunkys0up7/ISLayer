"""Tests for the Phase 4 report builder."""
from __future__ import annotations

import json
from pathlib import Path

from triple_flow_sim.components.c13_reports import (
    ReportBuilder,
    render_backlog,
    render_heatmap,
    render_regression_delta,
    render_triple_dossier,
)
from triple_flow_sim.contracts import (
    Confidence,
    DefectClass,
    Evidence,
    Finding,
    FindingStatus,
    Generator,
    Layer,
    Severity,
)


def _finding(
    defect: DefectClass,
    severity: Severity = Severity.CORRECTNESS,
    layer: Layer = Layer.PIM,
    triple: str = "T1",
    count: int = 1,
    on_critical: bool = False,
    fid: str = "f1",
) -> Finding:
    return Finding(
        finding_id=fid,
        taxonomy_version="1.0.0",
        layer=layer,
        defect_class=defect,
        generator=Generator.INVENTORY,
        severity=severity,
        confidence=Confidence.HIGH,
        primary_triple_id=triple,
        bpmn_node_id="n1",
        summary=f"{defect.value} on {triple}",
        detail="",
        evidence=Evidence(),
        journeys_affected_count=count,
        journeys_affected_pct=count * 10.0,
        is_on_critical_path=on_critical,
        status=FindingStatus.NEW,
    )


def test_backlog_orders_regulatory_first():
    reg = _finding(DefectClass.REGULATORY_VIOLATION, Severity.REGULATORY, fid="f1")
    cosm = _finding(DefectClass.HANDOFF_NAMING_DRIFT, Severity.COSMETIC, fid="f2")
    out = render_backlog([cosm, reg])
    # regulatory row appears before cosmetic row
    idx_reg = out.find("regulatory_violation")
    idx_cosm = out.find("handoff_naming_drift")
    assert idx_reg < idx_cosm


def test_heatmap_matrix_counts():
    f1 = _finding(DefectClass.CONTRACT_MISSING, layer=Layer.PIM, fid="f1")
    f2 = _finding(DefectClass.CONTRACT_MISSING, layer=Layer.PIM, fid="f2")
    f3 = _finding(DefectClass.CONTENT_MISSING, layer=Layer.PSM, fid="f3")
    matrix = render_heatmap([f1, f2, f3])
    assert matrix["matrix"]["contract_missing"]["PIM"] == 2
    assert matrix["matrix"]["content_missing"]["PSM"] == 1
    assert matrix["totals_by_class"]["contract_missing"] == 2


def test_regression_delta_shows_new_and_resolved():
    prev = [_finding(DefectClass.CONTRACT_MISSING, fid="fA")]
    cur = [_finding(DefectClass.CONTENT_MISSING, fid="fB")]
    out = render_regression_delta(cur, prev)
    assert "New findings: 1" in out
    assert "Resolved findings: 1" in out
    assert "content_missing" in out
    assert "contract_missing" in out


def test_dossier_includes_related_findings():
    f_primary = _finding(DefectClass.CONTRACT_MISSING, triple="T1", fid="f1")
    f_related = _finding(DefectClass.HANDOFF_IMPLICIT_SETUP, triple="T2", fid="f2")
    f_related.related_triple_ids = ["T1"]
    out = render_triple_dossier("T1", [f_primary, f_related])
    assert "contract_missing" in out
    assert "handoff_implicit_setup" in out


def test_report_builder_writes_files(tmp_path: Path):
    rb = ReportBuilder(tmp_path / "reports")
    f1 = _finding(DefectClass.CONTRACT_MISSING, fid="f1")
    paths = rb.write_all(
        findings=[f1],
        previous_findings=[],
        triple_ids=["T1"],
    )
    assert paths["backlog"].exists()
    assert paths["heatmap"].exists()
    assert paths["regression"].exists()
    assert (tmp_path / "reports" / "dossier" / "T1.md").exists()
    # heatmap is JSON
    data = json.loads(paths["heatmap"].read_text(encoding="utf-8"))
    assert "matrix" in data
