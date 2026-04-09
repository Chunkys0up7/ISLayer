"""Unit tests for the scoring algorithm in cli/pipeline/stage2_enricher.py."""

import importlib.util
import os
import pytest

# Load the module via importlib to access private functions
_enricher_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "cli",
    "pipeline",
    "stage2_enricher.py",
)
spec = importlib.util.spec_from_file_location("stage2_enricher", _enricher_path)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

_score_corpus_matches = mod._score_corpus_matches
_generate_gaps = mod._generate_gaps

from models.bpmn import ParsedModel, BpmnNode, BpmnProcess
from models.enriched import (
    NodeEnrichment,
    ProcedureEnrichment,
    OwnershipEnrichment,
    DecisionRuleEnrichment,
    GapType,
    GapSeverity,
)
from models.corpus import CorpusIndex, CorpusIndexEntry, AppliesTo


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_node(
    node_id="Task_Verify",
    name="Verify Income",
    element_type="serviceTask",
    lane_name=None,
):
    return BpmnNode(
        id=node_id,
        name=name,
        element_type=element_type,
        lane_name=lane_name,
    )


def _make_parsed_model(node, process_id="Process_LoanOrigination", process_name="Loan Origination"):
    return ParsedModel(
        processes=[BpmnProcess(id=process_id, name=process_name)],
        nodes=[node],
    )


def _make_entry(
    corpus_id="CRP-PRC-MTG-001",
    doc_type="procedure",
    domain="Mortgage Lending",
    process_ids=None,
    task_name_patterns=None,
    task_types=None,
    tags=None,
    roles=None,
):
    return CorpusIndexEntry(
        corpus_id=corpus_id,
        title="Test Document",
        doc_type=doc_type,
        domain=domain,
        subdomain=None,
        path="test.corpus.md",
        tags=tags or [],
        applies_to=AppliesTo(
            process_ids=process_ids or [],
            task_types=task_types or [],
            task_name_patterns=task_name_patterns or [],
            roles=roles or [],
        ),
        status="current",
    )


def _make_index(entries):
    return CorpusIndex(
        version="1.0",
        generated_date="2026-04-09",
        document_count=len(entries),
        documents=entries,
    )


# ---------------------------------------------------------------------------
# Factor 1: Exact ID match (process_id + task_name_pattern)
# ---------------------------------------------------------------------------

class TestExactIdMatch:
    """Process ID + task name pattern match yields score 1.0 and method exact_id."""

    def test_exact_id(self):
        node = _make_node()
        model = _make_parsed_model(node)
        entry = _make_entry(
            process_ids=["Process_LoanOrigination"],
            task_name_patterns=[".*Verify.*"],
        )
        index = _make_index([entry])
        results = _score_corpus_matches(node, index, "Loan Origination", model)
        assert len(results) == 1
        assert results[0].match_score == 1.0
        assert results[0].match_method == "exact_id"


# ---------------------------------------------------------------------------
# Factor: Name pattern only
# ---------------------------------------------------------------------------

class TestNamePatternOnly:
    """Name pattern match without process ID yields score 0.8 and method name_pattern."""

    def test_name_pattern(self):
        node = _make_node()
        model = _make_parsed_model(node)
        entry = _make_entry(
            process_ids=["Process_Other"],  # no match
            task_name_patterns=[".*Verify.*"],
        )
        index = _make_index([entry])
        results = _score_corpus_matches(node, index, "Loan Origination", model)
        assert len(results) == 1
        assert results[0].match_score == 0.8
        assert results[0].match_method == "name_pattern"


# ---------------------------------------------------------------------------
# Factor: Domain + task type
# ---------------------------------------------------------------------------

class TestDomainTaskType:
    """Domain + task type match yields score 0.5 and method domain_type."""

    def test_domain_type(self):
        node = _make_node(name="Some Task")  # name won't match patterns
        model = _make_parsed_model(node)
        entry = _make_entry(
            task_types=["serviceTask"],
            domain="Loan Origination",  # matches process_domain
        )
        index = _make_index([entry])
        results = _score_corpus_matches(node, index, "Loan Origination", model)
        assert len(results) == 1
        assert results[0].match_score == 0.5
        assert results[0].match_method == "domain_type"


# ---------------------------------------------------------------------------
# Factor: Tag intersection
# ---------------------------------------------------------------------------

class TestTagIntersection:
    """Tag overlap with node name tokens yields score 0.3 and method tag_intersection."""

    def test_tag_intersection(self):
        node = _make_node(name="Verify Income")
        model = _make_parsed_model(node)
        entry = _make_entry(
            tags=["verify", "documents"],
            domain="Other Domain",  # no domain match
        )
        index = _make_index([entry])
        results = _score_corpus_matches(node, index, "Loan Origination", model)
        assert len(results) == 1
        assert results[0].match_score >= 0.3
        assert results[0].match_method == "tag_intersection"


# ---------------------------------------------------------------------------
# Factor: Role bonus
# ---------------------------------------------------------------------------

class TestRoleBonus:
    """Role match adds +0.1 to the score."""

    def test_role_bonus(self):
        node = _make_node(lane_name="Underwriter")
        model = _make_parsed_model(node)
        entry = _make_entry(
            process_ids=["Process_LoanOrigination"],
            task_name_patterns=[".*Verify.*"],
            roles=["Underwriter"],
        )
        index = _make_index([entry])
        results = _score_corpus_matches(node, index, "Loan Origination", model)
        assert len(results) == 1
        # 1.0 (exact_id) + 0.1 (role) = 1.1
        assert results[0].match_score == pytest.approx(1.1)


# ---------------------------------------------------------------------------
# Below threshold excluded
# ---------------------------------------------------------------------------

class TestBelowThresholdExcluded:
    """Entries scoring below 0.3 are excluded from results."""

    def test_below_threshold(self):
        node = _make_node(name="Some Task")
        model = _make_parsed_model(node)
        entry = _make_entry(
            domain="Completely Different",
            tags=["unrelated"],
        )
        index = _make_index([entry])
        results = _score_corpus_matches(node, index, "Loan Origination", model)
        assert len(results) == 0


# ---------------------------------------------------------------------------
# Results sorted by score descending
# ---------------------------------------------------------------------------

class TestResultsSortedByScore:
    """Results are sorted from highest to lowest score."""

    def test_sorted_descending(self):
        node = _make_node(name="Verify Income", lane_name="Underwriter")
        model = _make_parsed_model(node)
        entries = [
            _make_entry(
                corpus_id="CRP-1",
                tags=["verify"],  # tag_intersection -> 0.3
                domain="Other",
            ),
            _make_entry(
                corpus_id="CRP-2",
                process_ids=["Process_LoanOrigination"],
                task_name_patterns=[".*Verify.*"],  # exact_id -> 1.0
            ),
        ]
        index = _make_index(entries)
        results = _score_corpus_matches(node, index, "Loan Origination", model)
        assert len(results) == 2
        assert results[0].match_score >= results[1].match_score
        assert results[0].corpus_id == "CRP-2"


# ---------------------------------------------------------------------------
# doc_type_filter
# ---------------------------------------------------------------------------

class TestDocTypeFilter:
    """doc_type_filter excludes entries that do not match the filter."""

    def test_filter(self):
        node = _make_node()
        model = _make_parsed_model(node)
        entries = [
            _make_entry(
                corpus_id="CRP-PROC",
                doc_type="procedure",
                process_ids=["Process_LoanOrigination"],
                task_name_patterns=[".*Verify.*"],
            ),
            _make_entry(
                corpus_id="CRP-REG",
                doc_type="regulation",
                process_ids=["Process_LoanOrigination"],
                task_name_patterns=[".*Verify.*"],
            ),
        ]
        index = _make_index(entries)
        results = _score_corpus_matches(
            node, index, "Loan Origination", model, doc_type_filter="procedure"
        )
        assert len(results) == 1
        assert results[0].corpus_id == "CRP-PROC"


# ---------------------------------------------------------------------------
# Confidence levels
# ---------------------------------------------------------------------------

class TestConfidenceLevels:
    """Match confidence maps: >=0.8 high, >=0.5 medium, >=0.3 low."""

    def test_confidence_high(self):
        node = _make_node()
        model = _make_parsed_model(node)
        entry = _make_entry(
            process_ids=["Process_LoanOrigination"],
            task_name_patterns=[".*Verify.*"],
        )
        index = _make_index([entry])
        results = _score_corpus_matches(node, index, "Loan Origination", model)
        assert results[0].match_confidence == "high"

    def test_confidence_medium(self):
        node = _make_node(name="Some Task")
        model = _make_parsed_model(node)
        entry = _make_entry(
            task_types=["serviceTask"],
            domain="Loan Origination",
        )
        index = _make_index([entry])
        results = _score_corpus_matches(node, index, "Loan Origination", model)
        assert results[0].match_confidence == "medium"

    def test_confidence_low(self):
        node = _make_node(name="Verify Income")
        model = _make_parsed_model(node)
        entry = _make_entry(
            tags=["verify"],
            domain="Other",
        )
        index = _make_index([entry])
        results = _score_corpus_matches(node, index, "Loan Origination", model)
        assert results[0].match_confidence == "low"


# ---------------------------------------------------------------------------
# Gap generation
# ---------------------------------------------------------------------------

class TestGapMissingProcedure:
    """Missing procedure generates a HIGH severity gap."""

    def test_gap(self):
        node = _make_node(name="Test Task")
        ne = NodeEnrichment(node_id=node.id)
        # procedure.found is False by default
        gaps = _generate_gaps(node, ne)
        proc_gaps = [g for g in gaps if g.gap_type == GapType.MISSING_PROCEDURE]
        assert len(proc_gaps) == 1
        assert proc_gaps[0].severity == GapSeverity.HIGH


class TestGapMissingOwner:
    """Missing owner generates a HIGH severity gap."""

    def test_gap(self):
        node = _make_node(name="Test Task")
        ne = NodeEnrichment(node_id=node.id)
        # ownership.resolved is False by default
        gaps = _generate_gaps(node, ne)
        owner_gaps = [g for g in gaps if g.gap_type == GapType.MISSING_OWNER]
        assert len(owner_gaps) == 1
        assert owner_gaps[0].severity == GapSeverity.HIGH


class TestGapGatewayNoRules:
    """Gateway with no decision rules generates a CRITICAL severity gap."""

    def test_gap(self):
        node = _make_node(
            node_id="GW_1",
            name="Check Result",
            element_type="exclusiveGateway",
        )
        ne = NodeEnrichment(
            node_id=node.id,
            decision_rules=DecisionRuleEnrichment(defined=False),
        )
        gaps = _generate_gaps(node, ne)
        rule_gaps = [g for g in gaps if g.gap_type == GapType.MISSING_DECISION_RULES]
        assert len(rule_gaps) == 1
        assert rule_gaps[0].severity == GapSeverity.CRITICAL


class TestGapUnnamedElement:
    """An element with no name generates a MEDIUM severity gap."""

    def test_gap(self):
        node = _make_node(node_id="Task_X", name=None, element_type="task")
        ne = NodeEnrichment(node_id=node.id)
        gaps = _generate_gaps(node, ne)
        unnamed_gaps = [g for g in gaps if g.gap_type == GapType.UNNAMED_ELEMENT]
        assert len(unnamed_gaps) == 1
        assert unnamed_gaps[0].severity == GapSeverity.MEDIUM
