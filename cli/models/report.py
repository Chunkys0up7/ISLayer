"""Report data models for GAP analysis and health scoring."""
from dataclasses import dataclass, field
from typing import Optional
from enum import Enum


class HealthGrade(str, Enum):
    A = "A"
    B = "B"
    C = "C"
    D = "D"
    F = "F"


def grade_from_score(score: float) -> HealthGrade:
    if score >= 90: return HealthGrade.A
    if score >= 80: return HealthGrade.B
    if score >= 70: return HealthGrade.C
    if score >= 60: return HealthGrade.D
    return HealthGrade.F


def grade_label(grade: HealthGrade) -> str:
    return {"A": "Excellent", "B": "Good", "C": "Acceptable", "D": "Needs Work", "F": "Critical"}[grade.value]


@dataclass
class DimensionScore:
    name: str  # completeness, consistency, schema_compliance, knowledge_coverage, anti_ui_compliance
    score: float  # 0-100
    weight: float  # 0.0-1.0
    details: list[str] = field(default_factory=list)  # what was deducted and why


@dataclass
class GapEntry:
    gap_type: str
    severity: str  # critical, high, medium, low
    description: str
    triple_id: str
    source: str  # "capsule_frontmatter" or "gap_file"


@dataclass
class TripleFileInfo:
    artifact_type: str  # capsule, intent, contract
    artifact_id: str
    status: str
    binding_status: Optional[str] = None  # only for contracts


@dataclass
class TripleScore:
    triple_id: str
    triple_name: str
    bpmn_task_type: str
    health_score: float
    grade: HealthGrade
    dimensions: list[DimensionScore] = field(default_factory=list)
    gaps: list[GapEntry] = field(default_factory=list)
    files: list[TripleFileInfo] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "triple_id": self.triple_id,
            "name": self.triple_name,
            "type": self.bpmn_task_type,
            "health_score": round(self.health_score, 1),
            "grade": self.grade.value,
            "dimensions": [{"name": d.name, "score": round(d.score, 1), "weight": d.weight, "details": d.details} for d in self.dimensions],
            "gaps": [{"type": g.gap_type, "severity": g.severity, "description": g.description} for g in self.gaps],
            "files": [{"type": f.artifact_type, "id": f.artifact_id, "status": f.status, "binding": f.binding_status} for f in self.files],
        }


@dataclass
class GapSummary:
    total: int = 0
    critical: int = 0
    high: int = 0
    medium: int = 0
    low: int = 0

    def to_dict(self) -> dict:
        return {"total": self.total, "critical": self.critical, "high": self.high, "medium": self.medium, "low": self.low}


@dataclass
class CorpusCoverage:
    matched_docs: int = 0
    total_corpus_docs: int = 0
    triples_with_corpus_refs: int = 0

    def to_dict(self) -> dict:
        return {"matched_docs": self.matched_docs, "total_corpus_docs": self.total_corpus_docs, "triples_with_corpus_refs": self.triples_with_corpus_refs}


@dataclass
class GraphIntegrity:
    connected: bool = True
    cycles: bool = False
    start_events: int = 0
    end_events: int = 0

    def to_dict(self) -> dict:
        return {"connected": self.connected, "cycles": self.cycles, "start_events": self.start_events, "end_events": self.end_events}


@dataclass
class ProcessReport:
    process_id: str
    process_name: str
    generated: str  # ISO timestamp
    health_score: float
    grade: HealthGrade
    grade_label: str
    gap_summary: GapSummary = field(default_factory=GapSummary)
    schema_violations: int = 0
    cross_ref_errors: int = 0
    triple_scores: list[TripleScore] = field(default_factory=list)
    corpus_coverage: CorpusCoverage = field(default_factory=CorpusCoverage)
    graph_integrity: GraphIntegrity = field(default_factory=GraphIntegrity)

    def to_dict(self) -> dict:
        return {
            "process_id": self.process_id,
            "process_name": self.process_name,
            "generated": self.generated,
            "health_score": round(self.health_score, 1),
            "grade": self.grade.value,
            "grade_label": self.grade_label,
            "gap_summary": self.gap_summary.to_dict(),
            "schema_violations": self.schema_violations,
            "cross_ref_errors": self.cross_ref_errors,
            "total_triples": len(self.triple_scores),
            "triple_scores": [t.to_dict() for t in self.triple_scores],
            "corpus_coverage": self.corpus_coverage.to_dict(),
            "graph_integrity": self.graph_integrity.to_dict(),
        }
