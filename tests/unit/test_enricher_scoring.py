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
_DEFAULT_ENRICHMENT_CONFIG = mod._DEFAULT_ENRICHMENT_CONFIG

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
    subdomain=None,
    process_ids=None,
    task_name_patterns=None,
    task_types=None,
    tags=None,
    roles=None,
    goal_types=None,
):
    return CorpusIndexEntry(
        corpus_id=corpus_id,
        title="Test Document",
        doc_type=doc_type,
        domain=domain,
        subdomain=subdomain,
        path="test.corpus.md",
        tags=tags or [],
        applies_to=AppliesTo(
            process_ids=process_ids or [],
            task_types=task_types or [],
            task_name_patterns=task_name_patterns or [],
            roles=roles or [],
            goal_types=goal_types or [],
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


def _score(node, index, process_domain, model, doc_type_filter=None):
    """Convenience wrapper that supplies the new required parameters."""
    ecfg = {**_DEFAULT_ENRICHMENT_CONFIG}
    # Deep-copy nested dicts so tests don't mutate shared state
    for key in ("weights", "doc_type_relevance_scores"):
        ecfg[key] = {**_DEFAULT_ENRICHMENT_CONFIG[key]}
    return _score_corpus_matches(
        node,
        index,
        {},                     # corpus_bodies (empty for tests)
        process_domain,
        model,
        ecfg,
        set(),                  # matched_so_far
        set(),                  # node_data_refs
        "data_production",      # node_goal_type
        doc_type_filter=doc_type_filter,
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
        results = _score(node, index, "Loan Origination", model)
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
        results = _score(node, index, "Loan Origination", model)
        assert len(results) == 1
        assert results[0].match_score == 0.8
        assert results[0].match_method == "name_pattern"


# ---------------------------------------------------------------------------
# Factor: Weighted multi-signal (subdomain + tags + doc_type)
# ---------------------------------------------------------------------------

class TestWeightedMultiSignal:
    """Subdomain + tag overlap + doc_type yields a weighted score and method weighted_multi_signal."""

    def test_subdomain_and_tags(self):
        # Subdomain "Loan Origination" matches process_domain "Loan Origination"
        # Tags ["verify", "income"] match node name "Verify Income" tokens
        # doc_type "procedure" has relevance 1.0
        # Expected: subdomain 0.25 + tag_ratio 0.20*(2/2) + doc_type 0.15*1.0 = 0.60
        node = _make_node(name="Verify Income")
        model = _make_parsed_model(node)
        entry = _make_entry(
            subdomain="Loan Origination",
            tags=["verify", "income"],
            domain="Mortgage Lending",
        )
        index = _make_index([entry])
        results = _score(node, index, "Loan Origination", model)
        assert len(results) == 1
        assert results[0].match_score >= 0.4
        assert results[0].match_method == "weighted_multi_signal"


# ---------------------------------------------------------------------------
# Factor: Tag overlap (with subdomain to reach threshold)
# ---------------------------------------------------------------------------

class TestTagOverlap:
    """Tag overlap contributes to weighted score."""

    def test_tag_overlap_with_subdomain(self):
        # Tags ["verify"] match 1 of 2 node tokens ("verify", "income")
        # Subdomain match to push above threshold
        # tag_ratio = 0.20 * (1/2) = 0.10, subdomain = 0.25, doc_type = 0.15 = 0.50
        node = _make_node(name="Verify Income")
        model = _make_parsed_model(node)
        entry = _make_entry(
            subdomain="Loan Origination",
            tags=["verify"],
            domain="Other",
        )
        index = _make_index([entry])
        results = _score(node, index, "Loan Origination", model)
        assert len(results) == 1
        assert results[0].match_score >= 0.4
        assert results[0].match_method == "weighted_multi_signal"


# ---------------------------------------------------------------------------
# Factor: Role match in weighted scoring
# ---------------------------------------------------------------------------

class TestRoleInWeightedScoring:
    """Role match adds weight in tier 2 scoring."""

    def test_role_match_contributes(self):
        # Subdomain match + role match + doc_type
        # subdomain=0.25, role=0.10, doc_type=0.15*1.0=0.15 → total=0.50
        node = _make_node(name="Some Task", lane_name="Underwriter")
        model = _make_parsed_model(node)
        entry = _make_entry(
            subdomain="Loan Origination",
            roles=["Underwriter"],
            domain="Mortgage Lending",
        )
        index = _make_index([entry])
        results = _score(node, index, "Loan Origination", model)
        assert len(results) == 1
        assert results[0].match_score >= 0.4
        assert results[0].match_method == "weighted_multi_signal"

    def test_exact_id_ignores_tier2_role(self):
        """When tier 1 gives exact_id (1.0), tier 2 is skipped so role doesn't add."""
        node = _make_node(lane_name="Underwriter")
        model = _make_parsed_model(node)
        entry = _make_entry(
            process_ids=["Process_LoanOrigination"],
            task_name_patterns=[".*Verify.*"],
            roles=["Underwriter"],
        )
        index = _make_index([entry])
        results = _score(node, index, "Loan Origination", model)
        assert len(results) == 1
        # exact_id yields 1.0; tier 2 is skipped for score == 1.0
        assert results[0].match_score == 1.0
        assert results[0].match_method == "exact_id"


# ---------------------------------------------------------------------------
# Below threshold excluded
# ---------------------------------------------------------------------------

class TestBelowThresholdExcluded:
    """Entries scoring below 0.4 threshold are excluded from results."""

    def test_below_threshold(self):
        node = _make_node(name="Some Task")
        model = _make_parsed_model(node)
        entry = _make_entry(
            domain="Completely Different",
            tags=["unrelated"],
        )
        index = _make_index([entry])
        results = _score(node, index, "Loan Origination", model)
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
                subdomain="Loan Origination",
                tags=["verify"],  # weighted_multi_signal
                domain="Other",
            ),
            _make_entry(
                corpus_id="CRP-2",
                process_ids=["Process_LoanOrigination"],
                task_name_patterns=[".*Verify.*"],  # exact_id -> 1.0
            ),
        ]
        index = _make_index(entries)
        results = _score(node, index, "Loan Origination", model)
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
        results = _score(
            node, index, "Loan Origination", model, doc_type_filter="procedure"
        )
        assert len(results) == 1
        assert results[0].corpus_id == "CRP-PROC"


# ---------------------------------------------------------------------------
# Confidence levels
# ---------------------------------------------------------------------------

class TestConfidenceLevels:
    """Match confidence maps: >=0.8 high, >=0.5 medium, >=0.4 low."""

    def test_confidence_high(self):
        node = _make_node()
        model = _make_parsed_model(node)
        entry = _make_entry(
            process_ids=["Process_LoanOrigination"],
            task_name_patterns=[".*Verify.*"],
        )
        index = _make_index([entry])
        results = _score(node, index, "Loan Origination", model)
        assert results[0].match_confidence == "high"

    def test_confidence_medium(self):
        # Subdomain + tags + doc_type to get ~0.60 (medium range: 0.5-0.8)
        node = _make_node(name="Verify Income")
        model = _make_parsed_model(node)
        entry = _make_entry(
            subdomain="Loan Origination",
            tags=["verify", "income"],
            domain="Mortgage Lending",
        )
        index = _make_index([entry])
        results = _score(node, index, "Loan Origination", model)
        assert len(results) == 1
        assert results[0].match_confidence == "medium"

    def test_confidence_low(self):
        # Just enough to cross 0.4 threshold but below 0.5
        # subdomain=0.25 + doc_type=0.15*1.0=0.15 → 0.40 (at threshold, low confidence)
        node = _make_node(name="Some Task")
        model = _make_parsed_model(node)
        entry = _make_entry(
            subdomain="Loan Origination",
            domain="Other",
        )
        index = _make_index([entry])
        results = _score(node, index, "Loan Origination", model)
        assert len(results) == 1
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
