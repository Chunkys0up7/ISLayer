"""Job Aid data models — structured condition/action lookup tables."""
from dataclasses import dataclass, field
from typing import Any, Optional
from enum import Enum


class JobAidStatus(str, Enum):
    DRAFT = "draft"
    REVIEW = "review"
    CURRENT = "current"
    SUPERSEDED = "superseded"
    ARCHIVED = "archived"


class Precedence(str, Enum):
    FIRST_MATCH = "first_match"
    MOST_SPECIFIC = "most_specific"
    ALL_MATCHING = "all_matching"


@dataclass
class Dimension:
    name: str
    description: str = ""
    values: list[str] = field(default_factory=list)
    required_at_resolution: bool = True

    def to_dict(self): return {"name": self.name, "description": self.description, "values": self.values, "required_at_resolution": self.required_at_resolution}
    @classmethod
    def from_dict(cls, d): return cls(name=d["name"], description=d.get("description", ""), values=d.get("values", []), required_at_resolution=d.get("required_at_resolution", True))


@dataclass
class ActionField:
    name: str
    type: str  # string, number, boolean, string_array, object
    description: str = ""
    required: bool = True

    def to_dict(self): return {"name": self.name, "type": self.type, "description": self.description, "required": self.required}
    @classmethod
    def from_dict(cls, d): return cls(**{k: d[k] for k in ["name", "type"] if k in d}, description=d.get("description", ""), required=d.get("required", True))


@dataclass
class Rule:
    id: str
    conditions: dict[str, Any]  # dimension_name → value or list of values or "*"
    action: dict[str, Any]      # action_field_name → value
    notes: Optional[str] = None
    regulatory_ref: Optional[str] = None
    effective_date: Optional[str] = None
    expiry_date: Optional[str] = None

    def matches(self, query: dict[str, str]) -> bool:
        """Check if this rule matches the given condition query.

        A rule matches if every condition in the rule is satisfied:
        - Exact match: rule condition == query value
        - List match: query value is in the rule condition list
        - Wildcard: rule condition is "*" (matches anything)
        - Missing: if query doesn't have a dimension, rule condition is ignored
        """
        for dim_name, expected in self.conditions.items():
            if expected == "*" or expected is None:
                continue
            query_val = query.get(dim_name)
            if query_val is None:
                continue  # Dimension not specified in query — don't filter on it
            if isinstance(expected, list):
                if query_val not in expected:
                    return False
            elif query_val != expected:
                return False
        return True

    def specificity(self) -> int:
        """Count non-wildcard conditions (for most_specific precedence)."""
        return sum(1 for v in self.conditions.values() if v != "*" and v is not None)

    def to_dict(self):
        d = {"id": self.id, "conditions": self.conditions, "action": self.action}
        if self.notes: d["notes"] = self.notes
        if self.regulatory_ref: d["regulatory_ref"] = self.regulatory_ref
        if self.effective_date: d["effective_date"] = self.effective_date
        if self.expiry_date: d["expiry_date"] = self.expiry_date
        return d

    @classmethod
    def from_dict(cls, d):
        return cls(id=d["id"], conditions=d["conditions"], action=d["action"],
                   notes=d.get("notes"), regulatory_ref=d.get("regulatory_ref"),
                   effective_date=d.get("effective_date"), expiry_date=d.get("expiry_date"))


@dataclass
class JobAid:
    jobaid_id: str
    capsule_id: str
    title: str
    version: str = "1.0"
    status: JobAidStatus = JobAidStatus.DRAFT
    description: str = ""
    source_file: Optional[str] = None
    author: str = ""
    last_modified: str = ""
    last_modified_by: str = ""
    dimensions: list[Dimension] = field(default_factory=list)
    action_fields: list[ActionField] = field(default_factory=list)
    rules: list[Rule] = field(default_factory=list)
    default_action: Optional[dict] = None
    precedence: Precedence = Precedence.FIRST_MATCH
    file_path: Optional[str] = None

    def query(self, conditions: dict[str, str]) -> list[Rule]:
        """Find rules matching the given conditions.

        Returns rules based on the precedence strategy:
        - first_match: return only the first matching rule
        - most_specific: return the rule with the most non-wildcard conditions
        - all_matching: return all matching rules
        """
        matches = [r for r in self.rules if r.matches(conditions)]

        if not matches:
            return []

        if self.precedence == Precedence.FIRST_MATCH:
            return [matches[0]]
        elif self.precedence == Precedence.MOST_SPECIFIC:
            matches.sort(key=lambda r: r.specificity(), reverse=True)
            return [matches[0]]
        else:  # ALL_MATCHING
            return matches

    def get_rule(self, rule_id: str) -> Optional[Rule]:
        """Get a specific rule by ID."""
        for r in self.rules:
            if r.id == rule_id:
                return r
        return None

    @property
    def dimension_names(self) -> list[str]:
        return [d.name for d in self.dimensions]

    @property
    def rule_count(self) -> int:
        return len(self.rules)

    def to_dict(self) -> dict:
        d = {
            "jobaid_id": self.jobaid_id,
            "capsule_id": self.capsule_id,
            "title": self.title,
            "version": self.version,
            "status": self.status.value,
            "dimensions": [dim.to_dict() for dim in self.dimensions],
            "rules": [r.to_dict() for r in self.rules],
            "precedence": self.precedence.value,
        }
        if self.description: d["description"] = self.description
        if self.source_file: d["source_file"] = self.source_file
        if self.author: d["author"] = self.author
        if self.last_modified: d["last_modified"] = self.last_modified
        if self.last_modified_by: d["last_modified_by"] = self.last_modified_by
        if self.action_fields: d["action_fields"] = [af.to_dict() for af in self.action_fields]
        if self.default_action: d["default_action"] = self.default_action
        return d

    @classmethod
    def from_dict(cls, d: dict) -> 'JobAid':
        return cls(
            jobaid_id=d["jobaid_id"],
            capsule_id=d["capsule_id"],
            title=d["title"],
            version=d.get("version", "1.0"),
            status=JobAidStatus(d.get("status", "draft")),
            description=d.get("description", ""),
            source_file=d.get("source_file"),
            author=d.get("author", ""),
            last_modified=d.get("last_modified", ""),
            last_modified_by=d.get("last_modified_by", ""),
            dimensions=[Dimension.from_dict(dim) for dim in d.get("dimensions", [])],
            action_fields=[ActionField.from_dict(af) for af in d.get("action_fields", [])],
            rules=[Rule.from_dict(r) for r in d.get("rules", [])],
            default_action=d.get("default_action"),
            precedence=Precedence(d.get("precedence", "first_match")),
        )
