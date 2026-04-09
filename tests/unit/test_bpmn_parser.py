"""Unit tests for cli/mda_io/bpmn_xml.py — BPMN 2.0 XML parser."""

import sys
import os
import pytest
from pathlib import Path
from collections import Counter

_TESTS_DIR = Path(__file__).parent.parent.resolve()
_PROJECT_ROOT = _TESTS_DIR.parent.resolve()
sys.path.insert(0, str(_PROJECT_ROOT / "cli"))

from mda_io.bpmn_xml import parse_bpmn

EXAMPLES_DIR = _PROJECT_ROOT / "examples"

EXPECTED = {
    "loan-origination": {"total_nodes": 13, "edges": 13, "data_objects": 4},
    "income-verification": {"total_nodes": 11},
    "property-appraisal": {"total_nodes": 12},
}


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def loan_model():
    path = EXAMPLES_DIR / "loan-origination" / "bpmn" / "loan-origination.bpmn"
    return parse_bpmn(path)


@pytest.fixture
def income_model():
    path = EXAMPLES_DIR / "income-verification" / "bpmn" / "income-verification.bpmn"
    return parse_bpmn(path)


@pytest.fixture
def property_model():
    path = EXAMPLES_DIR / "property-appraisal" / "bpmn" / "property-appraisal.bpmn"
    return parse_bpmn(path)


# ---------------------------------------------------------------------------
# Node counts
# ---------------------------------------------------------------------------

class TestLoanOriginationNodeCount:
    """Loan origination BPMN has 13 nodes."""

    def test_total_nodes(self, loan_model):
        assert len(loan_model.nodes) == EXPECTED["loan-origination"]["total_nodes"]


class TestLoanOriginationTypeDistribution:
    """Loan origination type distribution matches expected counts."""

    def test_type_distribution(self, loan_model):
        counts = Counter(n.element_type for n in loan_model.nodes)
        assert counts["task"] == 1
        assert counts["serviceTask"] == 2
        assert counts["businessRuleTask"] == 1
        assert counts["sendTask"] == 2
        assert counts["receiveTask"] == 1
        assert counts["exclusiveGateway"] == 2
        assert counts["startEvent"] == 1
        assert counts["endEvent"] == 2
        assert counts["boundaryEvent"] == 1


class TestIncomeVerificationNodeCount:
    """Income verification BPMN has 11 nodes."""

    def test_total_nodes(self, income_model):
        assert len(income_model.nodes) == EXPECTED["income-verification"]["total_nodes"]


class TestPropertyAppraisalNodeCount:
    """Property appraisal BPMN has 12 nodes."""

    def test_total_nodes(self, property_model):
        assert len(property_model.nodes) == EXPECTED["property-appraisal"]["total_nodes"]


# ---------------------------------------------------------------------------
# Lane assignment
# ---------------------------------------------------------------------------

class TestLaneAssignment:
    """All loan origination nodes have a lane_id assigned."""

    def test_all_nodes_have_lane(self, loan_model):
        for node in loan_model.nodes:
            assert node.lane_id is not None, f"Node {node.id} has no lane_id"


# ---------------------------------------------------------------------------
# Edge count and validity
# ---------------------------------------------------------------------------

class TestEdgeCount:
    """Loan origination has 13 edges."""

    def test_edge_count(self, loan_model):
        assert len(loan_model.edges) == EXPECTED["loan-origination"]["edges"]


class TestEdgeValidity:
    """All edge source/target IDs reference existing nodes."""

    def test_edge_source_target_exist(self, loan_model):
        node_ids = {n.id for n in loan_model.nodes}
        for edge in loan_model.edges:
            assert edge.source_id in node_ids, f"Edge {edge.id} source {edge.source_id} not in nodes"
            assert edge.target_id in node_ids, f"Edge {edge.id} target {edge.target_id} not in nodes"


# ---------------------------------------------------------------------------
# Boundary event
# ---------------------------------------------------------------------------

class TestBoundaryEventAttachment:
    """Boundary_Timeout is attached to Task_RequestDocs."""

    def test_boundary_attached_to(self, loan_model):
        boundary = loan_model.get_node("Boundary_Timeout")
        assert boundary is not None, "Boundary_Timeout node not found"
        assert boundary.attached_to == "Task_RequestDocs"


# ---------------------------------------------------------------------------
# Data objects
# ---------------------------------------------------------------------------

class TestDataObjects:
    """Loan origination has 4 data objects."""

    def test_data_object_count(self, loan_model):
        assert len(loan_model.data_objects) == EXPECTED["loan-origination"]["data_objects"]


# ---------------------------------------------------------------------------
# No duplicate IDs
# ---------------------------------------------------------------------------

class TestNoDuplicateIds:
    """No two nodes in a BPMN file share the same ID."""

    def test_no_duplicate_node_ids(self, loan_model):
        ids = [n.id for n in loan_model.nodes]
        assert len(ids) == len(set(ids)), f"Duplicate node IDs found: {[x for x in ids if ids.count(x) > 1]}"


# ---------------------------------------------------------------------------
# Process extraction
# ---------------------------------------------------------------------------

class TestProcessExtraction:
    """Process element is extracted with id, name, is_executable."""

    def test_process_attributes(self, loan_model):
        assert len(loan_model.processes) >= 1
        proc = loan_model.processes[0]
        assert proc.id == "Process_LoanOrigination"
        assert proc.name is not None
        assert isinstance(proc.is_executable, bool)


# ---------------------------------------------------------------------------
# Predecessor / successor helpers
# ---------------------------------------------------------------------------

class TestGetPredecessors:
    """get_predecessors returns expected predecessor nodes."""

    def test_predecessors(self, loan_model):
        preds = loan_model.get_predecessors("Task_VerifyIdentity")
        pred_ids = [p.id for p in preds]
        assert "Task_ReceiveApplication" in pred_ids


class TestGetSuccessors:
    """get_successors returns expected successor nodes."""

    def test_successors(self, loan_model):
        succs = loan_model.get_successors("Task_ReceiveApplication")
        succ_ids = [s.id for s in succs]
        assert "Task_VerifyIdentity" in succ_ids


# ---------------------------------------------------------------------------
# Error handling
# ---------------------------------------------------------------------------

class TestInvalidXmlRaisesError:
    """parse_bpmn raises ValueError on non-BPMN XML."""

    def test_invalid_xml(self, tmp_path):
        bad = tmp_path / "bad.bpmn"
        bad.write_text('<?xml version="1.0"?>\n<root><child/></root>', encoding="utf-8")
        with pytest.raises(ValueError, match="Not a valid BPMN"):
            parse_bpmn(bad)


class TestMissingFileRaisesError:
    """parse_bpmn raises an exception for a missing file."""

    def test_missing_file(self, tmp_path):
        missing = tmp_path / "does_not_exist.bpmn"
        with pytest.raises(Exception):
            parse_bpmn(missing)
