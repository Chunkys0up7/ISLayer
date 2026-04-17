"""Unit tests for FindingClassifier (component 11)."""
from __future__ import annotations

import pytest

from triple_flow_sim.components.c11_classifier import FindingClassifier
from triple_flow_sim.contracts import (
    DefectClass,
    Evidence,
    Generator,
    Layer,
    RawDetection,
)


def _classifier(strict: bool = True) -> FindingClassifier:
    return FindingClassifier(strict=strict)


def test_classify_missing_identity():
    c = _classifier()
    det = RawDetection(
        signal_type="missing_identity_field",
        generator=Generator.INVENTORY,
        primary_triple_id="t-001",
        detector_context={
            "missing_fields": ["bpmn_node_id"],
            "source_path": "corpus/t-001.yaml",
        },
        evidence=Evidence(observed={"missing_fields": ["bpmn_node_id"]}, trace_ref="t:inv"),
    )
    finding = c.classify(det, run_id="run-1")

    assert finding.defect_class == DefectClass.IDENTITY_INCOMPLETE
    assert finding.layer == Layer.NA
    assert "t-001" in finding.summary
    assert "bpmn_node_id" in finding.summary
    assert "corpus/t-001.yaml" in finding.detail


def test_classify_gateway_missing_predicates():
    c = _classifier()
    det = RawDetection(
        signal_type="gateway_missing_predicates",
        generator=Generator.INVENTORY,
        primary_triple_id="t-gw-001",
        bpmn_node_id="Gateway_1",
        detector_context={"bpmn_node_type": "exclusiveGateway"},
    )
    finding = c.classify(det, run_id="run-1")

    assert finding.defect_class == DefectClass.EVALUABILITY_GAP
    assert finding.layer == Layer.PIM
    assert "t-gw-001" in finding.summary
    assert "exclusiveGateway" in finding.detail


def test_classify_state_flow_gap():
    c = _classifier()
    det = RawDetection(
        signal_type="state_flow_gap",
        generator=Generator.INVENTORY,
        primary_triple_id="t-reader",
        detector_context={"path": "application.fico_score"},
    )
    finding = c.classify(det, run_id="run-1")

    assert finding.defect_class == DefectClass.STATE_FLOW_GAP
    assert finding.layer == Layer.PIM
    assert "application.fico_score" in finding.summary
    assert "t-reader" in finding.summary


def test_classify_unknown_signal_strict_raises():
    c = _classifier(strict=True)
    det = RawDetection(
        signal_type="totally_unknown_signal",
        generator=Generator.INVENTORY,
        primary_triple_id="t-x",
    )
    with pytest.raises(ValueError):
        c.classify(det, run_id="run-1")


def test_classify_unknown_signal_nonstrict_fallback():
    c = _classifier(strict=False)
    det = RawDetection(
        signal_type="totally_unknown_signal",
        generator=Generator.INVENTORY,
        primary_triple_id="t-x",
    )
    finding = c.classify(det, run_id="run-1")
    # Fallback returns a finding without raising.
    assert finding.primary_triple_id == "t-x"
    assert finding.defect_class in set(DefectClass)


def test_dedup_key_deterministic():
    c = _classifier()
    det = RawDetection(
        signal_type="state_flow_gap",
        generator=Generator.INVENTORY,
        primary_triple_id="t-reader",
        bpmn_edge_id="edge-7",
        detector_context={"path": "application.fico_score"},
        evidence=Evidence(observed={"path": "application.fico_score"}, trace_ref="t:inv"),
    )
    f1 = c.classify(det, run_id="run-1")
    f2 = c.classify(det, run_id="run-2")

    # Same (defect_class, primary_triple_id, bpmn_edge_id, observed) -> same dedup_key.
    assert c.dedup_key(f1) == c.dedup_key(f2)

    # Changing the observed value should change the key.
    det_diff = det.model_copy(update={"evidence": Evidence(observed={"path": "other.path"})})
    f_diff = c.classify(det_diff, run_id="run-1")
    assert c.dedup_key(f1) != c.dedup_key(f_diff)


def test_template_rendering_includes_detector_context():
    c = _classifier()
    det = RawDetection(
        signal_type="missing_contract_field",
        generator=Generator.INVENTORY,
        primary_triple_id="t-contract",
        detector_context={"field_name": "pim.postconditions"},
    )
    finding = c.classify(det, run_id="run-1")
    assert "t-contract" in finding.summary
    assert "pim.postconditions" in finding.summary
    assert "pim.postconditions" in finding.detail
