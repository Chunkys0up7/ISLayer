"""Unit tests for the MDA-format adapter.

Tests run against the live examples/income-verification/ corpus.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from triple_flow_sim.components.c01_loader.adapter_mda import (
    discover_triple_dirs,
    load_mda_triple,
    normalize_bpmn_type,
)
from triple_flow_sim.contracts.triple import BpmnNodeType


EXAMPLES_ROOT = (
    Path(__file__).parent.parent.parent.parent.parent
    / "examples"
    / "income-verification"
)


@pytest.fixture(scope="module")
def bpmn_xml() -> str:
    bpmn_file = next(iter((EXAMPLES_ROOT / "bpmn").glob("*.bpmn")))
    return bpmn_file.read_text(encoding="utf-8")


# -----------------------------------------------------------------------------
# normalize_bpmn_type
# -----------------------------------------------------------------------------

def test_normalize_bpmn_type_tasks():
    for s in (
        "serviceTask", "userTask", "businessRuleTask", "sendTask",
        "receiveTask", "task", "manualTask", "scriptTask",
    ):
        assert normalize_bpmn_type(s) == BpmnNodeType.TASK


def test_normalize_bpmn_type_gateways():
    assert normalize_bpmn_type("exclusiveGateway") == BpmnNodeType.EXCLUSIVE_GATEWAY
    assert normalize_bpmn_type("inclusiveGateway") == BpmnNodeType.EXCLUSIVE_GATEWAY
    assert normalize_bpmn_type("eventBasedGateway") == BpmnNodeType.EXCLUSIVE_GATEWAY
    assert normalize_bpmn_type("parallelGateway") == BpmnNodeType.PARALLEL_GATEWAY


def test_normalize_bpmn_type_events():
    assert normalize_bpmn_type("startEvent") == BpmnNodeType.START_EVENT
    assert normalize_bpmn_type("endEvent") == BpmnNodeType.END_EVENT
    assert normalize_bpmn_type("boundaryEvent") == BpmnNodeType.INTERMEDIATE_EVENT
    assert (
        normalize_bpmn_type("intermediateThrowEvent") == BpmnNodeType.INTERMEDIATE_EVENT
    )
    assert (
        normalize_bpmn_type("intermediateCatchEvent") == BpmnNodeType.INTERMEDIATE_EVENT
    )


def test_normalize_bpmn_type_unknown_defaults_to_task():
    assert normalize_bpmn_type("weirdUnknownNode") == BpmnNodeType.TASK
    assert normalize_bpmn_type("") == BpmnNodeType.TASK


# -----------------------------------------------------------------------------
# Load a single W-2 triple
# -----------------------------------------------------------------------------

def test_load_mda_triple_verify_w2():
    triple_dir = EXAMPLES_ROOT / "triples" / "verify-w2"
    triple, err = load_mda_triple(triple_dir)
    assert err is None, f"load failed: {err}"
    assert triple is not None

    assert triple.triple_id.startswith("CAP-IV-W2V")
    assert triple.bpmn_node_id == "Task_VerifyW2"
    assert triple.bpmn_node_type == BpmnNodeType.TASK

    assert triple.cim is not None
    assert triple.cim.intent  # non-empty goal

    assert triple.pim is not None
    assert triple.pim.state_reads is not None and len(triple.pim.state_reads) >= 1
    assert triple.pim.state_writes is not None and len(triple.pim.state_writes) >= 1
    # MDA format has no explicit postconditions — must stay None to surface I4.
    assert triple.pim.postconditions is None

    assert triple.psm is not None
    assert len(triple.psm.enriched_content) >= 1


# -----------------------------------------------------------------------------
# Gateway: decision predicates from BPMN XML
# -----------------------------------------------------------------------------

def test_load_mda_gateway(bpmn_xml: str):
    gateway_dir = EXAMPLES_ROOT / "decisions" / "employment-type"
    triple, err = load_mda_triple(gateway_dir, bpmn_content=bpmn_xml)
    assert err is None, f"load failed: {err}"
    assert triple is not None

    assert triple.bpmn_node_type == BpmnNodeType.EXCLUSIVE_GATEWAY
    assert triple.pim is not None
    assert triple.pim.decision_predicates is not None
    assert len(triple.pim.decision_predicates) >= 2

    exprs = {p.predicate_expression for p in triple.pim.decision_predicates}
    # Should contain both branch predicates stripped of ${...}
    assert any("employmentType" in e and "W2" in e for e in exprs)
    assert any("employmentType" in e and "SELF_EMPLOYED" in e for e in exprs)


def test_load_mda_gateway_without_bpmn_leaves_predicates_none():
    gateway_dir = EXAMPLES_ROOT / "decisions" / "employment-type"
    triple, err = load_mda_triple(gateway_dir, bpmn_content=None)
    assert err is None
    assert triple is not None
    assert triple.pim is not None
    assert triple.pim.decision_predicates is None


# -----------------------------------------------------------------------------
# Discovery
# -----------------------------------------------------------------------------

def test_discover_triple_dirs_income_verification():
    dirs = discover_triple_dirs(EXAMPLES_ROOT, ignore_paths=[])
    # 6 triples + 2 decisions = 8
    assert len(dirs) == 8, f"expected 8 triple dirs, got {len(dirs)}: {dirs}"
    names = {d.name for d in dirs}
    assert "verify-w2" in names
    assert "employment-type" in names
