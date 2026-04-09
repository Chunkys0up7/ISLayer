"""Dataclasses for Stage 2 enricher output."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from .bpmn import ParsedModel


class GapSeverity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class GapType(str, Enum):
    MISSING_PROCEDURE = "missing_procedure"
    MISSING_OWNER = "missing_owner"
    MISSING_DECISION_RULES = "missing_decision_rules"
    MISSING_DATA_SCHEMA = "missing_data_schema"
    MISSING_REGULATORY_CONTEXT = "missing_regulatory_context"
    MISSING_INTEGRATION_BINDING = "missing_integration_binding"
    AMBIGUOUS_NAME = "ambiguous_name"
    UNNAMED_ELEMENT = "unnamed_element"


@dataclass
class CorpusMatch:
    corpus_id: str
    match_confidence: str  # high, medium, low
    match_method: str  # exact_id, name_pattern, domain_type, tag_intersection
    match_score: float

    def to_dict(self) -> dict:
        return {
            "corpus_id": self.corpus_id,
            "match_confidence": self.match_confidence,
            "match_method": self.match_method,
            "match_score": self.match_score,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "CorpusMatch":
        return cls(
            corpus_id=data["corpus_id"],
            match_confidence=data["match_confidence"],
            match_method=data["match_method"],
            match_score=data["match_score"],
        )


@dataclass
class ProcedureEnrichment:
    found: bool
    corpus_refs: list[CorpusMatch] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "found": self.found,
            "corpus_refs": [c.to_dict() for c in self.corpus_refs],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ProcedureEnrichment":
        return cls(
            found=data["found"],
            corpus_refs=[
                CorpusMatch.from_dict(c) for c in data.get("corpus_refs", [])
            ],
        )


@dataclass
class OwnershipEnrichment:
    resolved: bool
    owner_role: Optional[str] = None
    owner_team: Optional[str] = None
    source: Optional[str] = None  # lane, participant, kb_mapping

    def to_dict(self) -> dict:
        return {
            "resolved": self.resolved,
            "owner_role": self.owner_role,
            "owner_team": self.owner_team,
            "source": self.source,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "OwnershipEnrichment":
        return cls(
            resolved=data["resolved"],
            owner_role=data.get("owner_role"),
            owner_team=data.get("owner_team"),
            source=data.get("source"),
        )


@dataclass
class DecisionRuleEnrichment:
    defined: bool
    rule_type: Optional[str] = None  # condition_expression, dmn_ref, kb_document, none
    rule_ref: Optional[str] = None
    conditions: list[dict] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "defined": self.defined,
            "rule_type": self.rule_type,
            "rule_ref": self.rule_ref,
            "conditions": [dict(c) for c in self.conditions],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "DecisionRuleEnrichment":
        return cls(
            defined=data["defined"],
            rule_type=data.get("rule_type"),
            rule_ref=data.get("rule_ref"),
            conditions=data.get("conditions", []),
        )


@dataclass
class DataSchemaEnrichment:
    data_ref: str
    schema_found: bool
    schema_ref: Optional[str] = None
    direction: Optional[str] = None  # input, output

    def to_dict(self) -> dict:
        return {
            "data_ref": self.data_ref,
            "schema_found": self.schema_found,
            "schema_ref": self.schema_ref,
            "direction": self.direction,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "DataSchemaEnrichment":
        return cls(
            data_ref=data["data_ref"],
            schema_found=data["schema_found"],
            schema_ref=data.get("schema_ref"),
            direction=data.get("direction"),
        )


@dataclass
class RegulatoryEnrichment:
    applicable: bool
    corpus_refs: list[CorpusMatch] = field(default_factory=list)
    regulation_refs: list[str] = field(default_factory=list)
    policy_refs: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "applicable": self.applicable,
            "corpus_refs": [c.to_dict() for c in self.corpus_refs],
            "regulation_refs": list(self.regulation_refs),
            "policy_refs": list(self.policy_refs),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "RegulatoryEnrichment":
        return cls(
            applicable=data["applicable"],
            corpus_refs=[
                CorpusMatch.from_dict(c) for c in data.get("corpus_refs", [])
            ],
            regulation_refs=data.get("regulation_refs", []),
            policy_refs=data.get("policy_refs", []),
        )


@dataclass
class IntegrationEnrichment:
    has_binding: bool
    system_name: Optional[str] = None
    protocol: Optional[str] = None
    endpoint_hint: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "has_binding": self.has_binding,
            "system_name": self.system_name,
            "protocol": self.protocol,
            "endpoint_hint": self.endpoint_hint,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "IntegrationEnrichment":
        return cls(
            has_binding=data["has_binding"],
            system_name=data.get("system_name"),
            protocol=data.get("protocol"),
            endpoint_hint=data.get("endpoint_hint"),
        )


@dataclass
class Gap:
    gap_id: str
    node_id: str
    gap_type: GapType
    severity: GapSeverity
    description: str
    suggested_resolution: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "gap_id": self.gap_id,
            "node_id": self.node_id,
            "gap_type": self.gap_type.value,
            "severity": self.severity.value,
            "description": self.description,
            "suggested_resolution": self.suggested_resolution,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Gap":
        return cls(
            gap_id=data["gap_id"],
            node_id=data["node_id"],
            gap_type=GapType(data["gap_type"]),
            severity=GapSeverity(data["severity"]),
            description=data["description"],
            suggested_resolution=data.get("suggested_resolution"),
        )


@dataclass
class NodeEnrichment:
    node_id: str
    procedure: ProcedureEnrichment = field(
        default_factory=lambda: ProcedureEnrichment(found=False)
    )
    ownership: OwnershipEnrichment = field(
        default_factory=lambda: OwnershipEnrichment(resolved=False)
    )
    decision_rules: Optional[DecisionRuleEnrichment] = None
    data_schemas: list[DataSchemaEnrichment] = field(default_factory=list)
    regulatory: RegulatoryEnrichment = field(
        default_factory=lambda: RegulatoryEnrichment(applicable=False)
    )
    integration: IntegrationEnrichment = field(
        default_factory=lambda: IntegrationEnrichment(has_binding=False)
    )

    def to_dict(self) -> dict:
        result: dict = {
            "node_id": self.node_id,
            "procedure": self.procedure.to_dict(),
            "ownership": self.ownership.to_dict(),
            "decision_rules": (
                self.decision_rules.to_dict()
                if self.decision_rules is not None
                else None
            ),
            "data_schemas": [ds.to_dict() for ds in self.data_schemas],
            "regulatory": self.regulatory.to_dict(),
            "integration": self.integration.to_dict(),
        }
        return result

    @classmethod
    def from_dict(cls, data: dict) -> "NodeEnrichment":
        dr_data = data.get("decision_rules")
        return cls(
            node_id=data["node_id"],
            procedure=ProcedureEnrichment.from_dict(data.get("procedure", {"found": False})),
            ownership=OwnershipEnrichment.from_dict(
                data.get("ownership", {"resolved": False})
            ),
            decision_rules=(
                DecisionRuleEnrichment.from_dict(dr_data) if dr_data is not None else None
            ),
            data_schemas=[
                DataSchemaEnrichment.from_dict(ds)
                for ds in data.get("data_schemas", [])
            ],
            regulatory=RegulatoryEnrichment.from_dict(
                data.get("regulatory", {"applicable": False})
            ),
            integration=IntegrationEnrichment.from_dict(
                data.get("integration", {"has_binding": False})
            ),
        )


@dataclass
class EnrichedModel:
    parsed_model: ParsedModel
    enrichment_date: str
    enriched_by: str
    node_enrichments: dict[str, NodeEnrichment] = field(default_factory=dict)
    gaps: list[Gap] = field(default_factory=list)

    def get_enrichment(self, node_id: str) -> Optional[NodeEnrichment]:
        """Get the enrichment record for a specific node."""
        return self.node_enrichments.get(node_id)

    def gap_summary(self) -> dict:
        """Return gap counts by severity and type."""
        by_severity: dict[str, int] = {}
        by_type: dict[str, int] = {}
        for gap in self.gaps:
            sev = gap.severity.value
            by_severity[sev] = by_severity.get(sev, 0) + 1
            gt = gap.gap_type.value
            by_type[gt] = by_type.get(gt, 0) + 1
        return {
            "total": len(self.gaps),
            "by_severity": by_severity,
            "by_type": by_type,
        }

    def to_dict(self) -> dict:
        """Serialize to a dict suitable for YAML/JSON output."""
        return {
            "parsed_model": self.parsed_model.to_dict(),
            "enrichment_date": self.enrichment_date,
            "enriched_by": self.enriched_by,
            "node_enrichments": {
                nid: ne.to_dict() for nid, ne in self.node_enrichments.items()
            },
            "gaps": [g.to_dict() for g in self.gaps],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "EnrichedModel":
        """Deserialize from a dict."""
        return cls(
            parsed_model=ParsedModel.from_dict(data["parsed_model"]),
            enrichment_date=data["enrichment_date"],
            enriched_by=data["enriched_by"],
            node_enrichments={
                nid: NodeEnrichment.from_dict(ne_data)
                for nid, ne_data in data.get("node_enrichments", {}).items()
            },
            gaps=[Gap.from_dict(g) for g in data.get("gaps", [])],
        )
