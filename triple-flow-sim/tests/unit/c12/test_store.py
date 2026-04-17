"""Unit tests for FindingStore (component 12). Phase 1 scope."""
from __future__ import annotations

from pathlib import Path

import pytest

from triple_flow_sim.components.c12_store import FindingStore
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


# --------------------------------------------------------------------- helpers

def _make_store(tmp_path: Path) -> FindingStore:
    return FindingStore(tmp_path / "findings.db")


def _start_run(store: FindingStore, run_id: str) -> None:
    store.start_run(
        run_id=run_id,
        corpus_version_hash="corpus-abc",
        bpmn_version_hash="bpmn-xyz",
        generator=Generator.INVENTORY.value,
        simulator_version="0.1.0",
        taxonomy_version="1.0.0",
        config={"mode": "test"},
    )


def _make_finding(
    *,
    primary_triple_id: str = "t-001",
    defect_class: DefectClass = DefectClass.IDENTITY_INCOMPLETE,
    observed: object = "missing-field-x",
    bpmn_edge_id: str | None = None,
    run_id: str = "run-1",
) -> Finding:
    return Finding(
        layer=Layer.NA,
        defect_class=defect_class,
        generator=Generator.INVENTORY,
        severity=Severity.CORRECTNESS,
        confidence=Confidence.HIGH,
        primary_triple_id=primary_triple_id,
        bpmn_node_id="node-1",
        bpmn_edge_id=bpmn_edge_id,
        summary=f"Test finding for {primary_triple_id}",
        detail="detail text",
        evidence=Evidence(observed=observed, trace_ref="t:test"),
        status=FindingStatus.NEW,
        first_seen_run=run_id,
        last_seen_run=run_id,
    )


# ----------------------------------------------------------------------- tests

def test_start_and_complete_run(tmp_path):
    store = _make_store(tmp_path)
    try:
        _start_run(store, "run-1")
        store.complete_run("run-1", metrics={"triples_loaded": 42, "findings": 3})

        row = store._conn.execute(
            "SELECT run_id, status, metrics_json FROM runs WHERE run_id = ?",
            ("run-1",),
        ).fetchone()
        assert row is not None
        assert row["run_id"] == "run-1"
        assert row["status"] == "completed"
        assert "triples_loaded" in row["metrics_json"]
        assert "42" in row["metrics_json"]
    finally:
        store.close()


def test_emit_finding_basic(tmp_path):
    store = _make_store(tmp_path)
    try:
        _start_run(store, "run-1")
        finding = _make_finding(primary_triple_id="t-001", run_id="run-1")
        finding_id = store.emit_finding(finding, run_id="run-1")

        assert finding_id

        results = store.findings_by_triple("t-001")
        assert len(results) == 1
        assert results[0].primary_triple_id == "t-001"
        assert results[0].defect_class == DefectClass.IDENTITY_INCOMPLETE
        assert results[0].occurrence_count == 1
    finally:
        store.close()


def test_emit_finding_dedup(tmp_path):
    store = _make_store(tmp_path)
    try:
        _start_run(store, "run-1")
        _start_run(store, "run-2")

        f1 = _make_finding(primary_triple_id="t-001", observed="same-obs", run_id="run-1")
        id1 = store.emit_finding(f1, run_id="run-1")

        # Re-emit identical finding in a different run.
        f2 = _make_finding(primary_triple_id="t-001", observed="same-obs", run_id="run-2")
        id2 = store.emit_finding(f2, run_id="run-2")

        # Same dedup key -> single findings row.
        assert id1 == id2

        results = store.findings_by_triple("t-001")
        assert len(results) == 1
        assert results[0].occurrence_count == 2
        assert results[0].last_seen_run == "run-2"
        assert results[0].first_seen_run == "run-1"

        # Two finding_occurrences rows.
        occ_count = store._conn.execute(
            "SELECT COUNT(*) AS n FROM finding_occurrences WHERE finding_id = ?",
            (id1,),
        ).fetchone()["n"]
        assert occ_count == 2

        # findings_by_run should surface the finding for both runs.
        assert len(store.findings_by_run("run-1")) == 1
        assert len(store.findings_by_run("run-2")) == 1
    finally:
        store.close()


def test_emit_finding_different_runs_different_triples(tmp_path):
    store = _make_store(tmp_path)
    try:
        _start_run(store, "run-1")

        f_a = _make_finding(primary_triple_id="t-001", observed="obs-a", run_id="run-1")
        f_b = _make_finding(primary_triple_id="t-002", observed="obs-b", run_id="run-1")

        id_a = store.emit_finding(f_a, run_id="run-1")
        id_b = store.emit_finding(f_b, run_id="run-1")
        assert id_a != id_b

        all_findings = store.get_findings()
        assert len(all_findings) == 2

        ids = {f.primary_triple_id for f in all_findings}
        assert ids == {"t-001", "t-002"}
    finally:
        store.close()
