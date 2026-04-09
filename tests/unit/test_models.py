"""Unit tests for cli/models/* — dataclass round-trips and enum coverage."""

import pytest

from models.bpmn import ParsedModel, BpmnNode, BpmnEdge, BpmnLane, BpmnProcess
from models.enriched import (
    EnrichedModel,
    NodeEnrichment,
    Gap,
    CorpusMatch,
    GapType,
    GapSeverity,
)
from models.triple import TripleStatus, GoalType, BindingStatus, CorpusRef
from models.corpus import (
    CorpusIndex,
    CorpusIndexEntry,
    AppliesTo,
    CorpusDocType,
    CorpusStatus,
)


# ---------------------------------------------------------------------------
# BpmnNode round-trip
# ---------------------------------------------------------------------------

class TestBpmnNodeRoundTrip:
    """BpmnNode serialises to dict and deserialises back identically."""

    def test_round_trip(self):
        node = BpmnNode(
            id="Task_1",
            name="Do Something",
            element_type="serviceTask",
            lane_id="Lane_A",
            lane_name="Operations",
            documentation="Performs an action",
        )
        d = node.to_dict()
        restored = BpmnNode.from_dict(d)
        assert restored.id == node.id
        assert restored.name == node.name
        assert restored.element_type == node.element_type
        assert restored.lane_id == node.lane_id
        assert restored.documentation == node.documentation


# ---------------------------------------------------------------------------
# BpmnEdge round-trip
# ---------------------------------------------------------------------------

class TestBpmnEdgeRoundTrip:
    """BpmnEdge serialises to dict and deserialises back identically."""

    def test_round_trip(self):
        edge = BpmnEdge(
            id="Flow_1",
            source_id="Task_A",
            target_id="Task_B",
            name="Approved",
            condition_expression="${approved}",
        )
        d = edge.to_dict()
        restored = BpmnEdge.from_dict(d)
        assert restored.id == edge.id
        assert restored.source_id == edge.source_id
        assert restored.condition_expression == edge.condition_expression


# ---------------------------------------------------------------------------
# ParsedModel round-trip
# ---------------------------------------------------------------------------

class TestParsedModelRoundTrip:
    """ParsedModel with processes/nodes/edges round-trips through dict."""

    def test_round_trip(self):
        model = ParsedModel(
            processes=[BpmnProcess(id="P1", name="Test Process", is_executable=True)],
            nodes=[
                BpmnNode(id="N1", name="Node 1", element_type="task"),
                BpmnNode(id="N2", name="Node 2", element_type="endEvent"),
            ],
            edges=[BpmnEdge(id="E1", source_id="N1", target_id="N2")],
            source_file="test.bpmn",
        )
        d = model.to_dict()
        restored = ParsedModel.from_dict(d)
        assert len(restored.processes) == 1
        assert len(restored.nodes) == 2
        assert len(restored.edges) == 1
        assert restored.source_file == "test.bpmn"


# ---------------------------------------------------------------------------
# get_node
# ---------------------------------------------------------------------------

class TestGetNode:
    """ParsedModel.get_node returns correct node or None."""

    def test_get_node_found(self):
        model = ParsedModel(
            nodes=[BpmnNode(id="N1", name="A", element_type="task")]
        )
        assert model.get_node("N1").name == "A"

    def test_get_node_not_found(self):
        model = ParsedModel(
            nodes=[BpmnNode(id="N1", name="A", element_type="task")]
        )
        assert model.get_node("MISSING") is None


# ---------------------------------------------------------------------------
# Enum values
# ---------------------------------------------------------------------------

class TestTripleStatusEnumValues:
    """TripleStatus enum has expected members."""

    def test_values(self):
        assert TripleStatus.DRAFT.value == "draft"
        assert TripleStatus.APPROVED.value == "approved"
        assert TripleStatus.CURRENT.value == "current"
        assert TripleStatus.DEPRECATED.value == "deprecated"
        assert TripleStatus.ARCHIVED.value == "archived"


class TestGoalTypeEnumValues:
    """GoalType enum has expected members."""

    def test_values(self):
        assert GoalType.DATA_PRODUCTION.value == "data_production"
        assert GoalType.DECISION.value == "decision"
        assert GoalType.NOTIFICATION.value == "notification"
        assert GoalType.STATE_TRANSITION.value == "state_transition"
        assert GoalType.ORCHESTRATION.value == "orchestration"


class TestBindingStatusEnum:
    """BindingStatus enum has expected members."""

    def test_values(self):
        assert BindingStatus.UNBOUND.value == "unbound"
        assert BindingStatus.PARTIAL.value == "partial"
        assert BindingStatus.BOUND.value == "bound"


class TestCorpusDocTypeEnum:
    """CorpusDocType enum has expected members."""

    def test_values(self):
        assert CorpusDocType.PROCEDURE.value == "procedure"
        assert CorpusDocType.POLICY.value == "policy"
        assert CorpusDocType.REGULATION.value == "regulation"
        assert CorpusDocType.RULE.value == "rule"
        assert CorpusDocType.DATA_DICTIONARY.value == "data-dictionary"
        assert CorpusDocType.SYSTEM.value == "system"


# ---------------------------------------------------------------------------
# CorpusIndex search
# ---------------------------------------------------------------------------

def _make_index():
    entries = [
        CorpusIndexEntry(
            corpus_id="CRP-PRC-MTG-001",
            title="Loan Application Intake",
            doc_type="procedure",
            domain="Mortgage Lending",
            subdomain="Origination",
            path="procedures/intake.corpus.md",
            tags=["loan", "intake"],
            applies_to=AppliesTo(),
            status="current",
        ),
        CorpusIndexEntry(
            corpus_id="CRP-REG-MTG-001",
            title="TRID Compliance Rules",
            doc_type="regulation",
            domain="Mortgage Lending",
            subdomain="Compliance",
            path="regulations/trid.corpus.md",
            tags=["trid", "compliance"],
            applies_to=AppliesTo(),
            status="current",
        ),
    ]
    return CorpusIndex(
        version="1.0",
        generated_date="2026-04-09",
        document_count=2,
        documents=entries,
    )


class TestCorpusIndexSearchByKeyword:
    """CorpusIndex.search finds entries matching a keyword in title/tags."""

    def test_search_keyword(self):
        idx = _make_index()
        results = idx.search("intake")
        assert len(results) == 1
        assert results[0].corpus_id == "CRP-PRC-MTG-001"


class TestCorpusIndexSearchWithTypeFilter:
    """CorpusIndex.search with doc_type filter excludes non-matching types."""

    def test_search_with_filter(self):
        idx = _make_index()
        # "Mortgage" matches both entries, but filter to regulation only
        results = idx.search("Mortgage", doc_type="regulation")
        assert len(results) == 1
        assert results[0].doc_type == "regulation"


# ---------------------------------------------------------------------------
# AppliesTo round-trip
# ---------------------------------------------------------------------------

class TestAppliesToRoundTrip:
    """AppliesTo serialises and deserialises correctly."""

    def test_round_trip(self):
        at = AppliesTo(
            process_ids=["P1"],
            task_types=["serviceTask"],
            task_name_patterns=[".*verify.*"],
            goal_types=["decision"],
            roles=["Underwriter"],
        )
        d = at.to_dict()
        restored = AppliesTo.from_dict(d)
        assert restored.process_ids == ["P1"]
        assert restored.roles == ["Underwriter"]


# ---------------------------------------------------------------------------
# Gap round-trip
# ---------------------------------------------------------------------------

class TestGapRoundTrip:
    """Gap serialises and deserialises correctly."""

    def test_round_trip(self):
        gap = Gap(
            gap_id="GAP-001",
            node_id="Task_X",
            gap_type=GapType.MISSING_PROCEDURE,
            severity=GapSeverity.HIGH,
            description="No procedure found",
            suggested_resolution="Create one",
        )
        d = gap.to_dict()
        restored = Gap.from_dict(d)
        assert restored.gap_id == "GAP-001"
        assert restored.gap_type == GapType.MISSING_PROCEDURE
        assert restored.severity == GapSeverity.HIGH


# ---------------------------------------------------------------------------
# gap_summary
# ---------------------------------------------------------------------------

class TestGapSummary:
    """EnrichedModel.gap_summary counts by severity and type correctly."""

    def test_gap_summary(self):
        gaps = [
            Gap("G1", "N1", GapType.MISSING_PROCEDURE, GapSeverity.HIGH, "desc"),
            Gap("G2", "N2", GapType.MISSING_OWNER, GapSeverity.HIGH, "desc"),
            Gap("G3", "N3", GapType.UNNAMED_ELEMENT, GapSeverity.MEDIUM, "desc"),
        ]
        model = EnrichedModel(
            parsed_model=ParsedModel(),
            enrichment_date="2026-04-09",
            enriched_by="test",
            gaps=gaps,
        )
        summary = model.gap_summary()
        assert summary["total"] == 3
        assert summary["by_severity"]["high"] == 2
        assert summary["by_severity"]["medium"] == 1
        assert summary["by_type"]["missing_procedure"] == 1
        assert summary["by_type"]["unnamed_element"] == 1


# ---------------------------------------------------------------------------
# EnrichedModel round-trip
# ---------------------------------------------------------------------------

class TestEnrichedModelRoundTrip:
    """EnrichedModel round-trips through dict."""

    def test_round_trip(self):
        pm = ParsedModel(
            nodes=[BpmnNode(id="N1", name="Test", element_type="task")],
            source_file="test.bpmn",
        )
        ne = NodeEnrichment(node_id="N1")
        em = EnrichedModel(
            parsed_model=pm,
            enrichment_date="2026-04-09",
            enriched_by="test",
            node_enrichments={"N1": ne},
            gaps=[
                Gap("G1", "N1", GapType.MISSING_PROCEDURE, GapSeverity.HIGH, "desc")
            ],
        )
        d = em.to_dict()
        restored = EnrichedModel.from_dict(d)
        assert len(restored.node_enrichments) == 1
        assert "N1" in restored.node_enrichments
        assert len(restored.gaps) == 1
        assert restored.enrichment_date == "2026-04-09"
