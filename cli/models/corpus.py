"""Dataclasses for corpus documents and the corpus index."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class CorpusDocType(str, Enum):
    PROCEDURE = "procedure"
    POLICY = "policy"
    REGULATION = "regulation"
    RULE = "rule"
    DATA_DICTIONARY = "data-dictionary"
    SYSTEM = "system"
    TRAINING = "training"
    GLOSSARY = "glossary"


class CorpusStatus(str, Enum):
    DRAFT = "draft"
    REVIEW = "review"
    CURRENT = "current"
    SUPERSEDED = "superseded"
    ARCHIVED = "archived"


@dataclass
class AppliesTo:
    process_ids: list[str] = field(default_factory=list)
    task_types: list[str] = field(default_factory=list)
    task_name_patterns: list[str] = field(default_factory=list)
    goal_types: list[str] = field(default_factory=list)
    roles: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "process_ids": list(self.process_ids),
            "task_types": list(self.task_types),
            "task_name_patterns": list(self.task_name_patterns),
            "goal_types": list(self.goal_types),
            "roles": list(self.roles),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "AppliesTo":
        return cls(
            process_ids=data.get("process_ids", []),
            task_types=data.get("task_types", []),
            task_name_patterns=data.get("task_name_patterns", []),
            goal_types=data.get("goal_types", []),
            roles=data.get("roles", []),
        )


@dataclass
class CorpusDocument:
    corpus_id: str
    title: str
    slug: str
    doc_type: CorpusDocType
    domain: str
    subdomain: Optional[str] = None
    tags: list[str] = field(default_factory=list)
    applies_to: AppliesTo = field(default_factory=AppliesTo)
    version: str = "1.0"
    status: CorpusStatus = CorpusStatus.CURRENT
    author: Optional[str] = None
    last_reviewed: Optional[str] = None
    supersedes: Optional[str] = None
    body: str = ""  # The markdown content below the frontmatter
    file_path: Optional[str] = None  # Where this was loaded from

    def to_dict(self) -> dict:
        return {
            "corpus_id": self.corpus_id,
            "title": self.title,
            "slug": self.slug,
            "doc_type": self.doc_type.value,
            "domain": self.domain,
            "subdomain": self.subdomain,
            "tags": list(self.tags),
            "applies_to": self.applies_to.to_dict(),
            "version": self.version,
            "status": self.status.value,
            "author": self.author,
            "last_reviewed": self.last_reviewed,
            "supersedes": self.supersedes,
            "body": self.body,
            "file_path": self.file_path,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "CorpusDocument":
        return cls(
            corpus_id=data["corpus_id"],
            title=data["title"],
            slug=data["slug"],
            doc_type=CorpusDocType(data["doc_type"]),
            domain=data["domain"],
            subdomain=data.get("subdomain"),
            tags=data.get("tags", []),
            applies_to=AppliesTo.from_dict(data.get("applies_to", {})),
            version=data.get("version", "1.0"),
            status=CorpusStatus(data.get("status", "current")),
            author=data.get("author"),
            last_reviewed=data.get("last_reviewed"),
            supersedes=data.get("supersedes"),
            body=data.get("body", ""),
            file_path=data.get("file_path"),
        )


@dataclass
class CorpusIndexEntry:
    corpus_id: str
    title: str
    doc_type: str
    domain: str
    subdomain: Optional[str]
    path: str
    tags: list[str]
    applies_to: AppliesTo
    status: str

    def to_dict(self) -> dict:
        return {
            "corpus_id": self.corpus_id,
            "title": self.title,
            "doc_type": self.doc_type,
            "domain": self.domain,
            "subdomain": self.subdomain,
            "path": self.path,
            "tags": list(self.tags),
            "applies_to": self.applies_to.to_dict(),
            "status": self.status,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "CorpusIndexEntry":
        return cls(
            corpus_id=data["corpus_id"],
            title=data["title"],
            doc_type=data["doc_type"],
            domain=data["domain"],
            subdomain=data.get("subdomain"),
            path=data["path"],
            tags=data.get("tags", []),
            applies_to=AppliesTo.from_dict(data.get("applies_to", {})),
            status=data["status"],
        )


@dataclass
class CorpusIndex:
    version: str
    generated_date: str
    document_count: int
    documents: list[CorpusIndexEntry] = field(default_factory=list)

    def search(
        self,
        query: str,
        doc_type: Optional[str] = None,
        domain: Optional[str] = None,
        tags: Optional[list[str]] = None,
    ) -> list[CorpusIndexEntry]:
        """Search index entries by keyword, type, domain, tags.

        The query string is matched case-insensitively against the title,
        corpus_id, domain, subdomain, and tags of each entry. Filters for
        doc_type, domain, and tags are applied as additional constraints.
        """
        query_lower = query.lower()
        results: list[CorpusIndexEntry] = []

        for entry in self.documents:
            # Apply hard filters first
            if doc_type is not None and entry.doc_type != doc_type:
                continue
            if domain is not None and entry.domain != domain:
                continue
            if tags is not None:
                entry_tags_lower = {t.lower() for t in entry.tags}
                if not all(t.lower() in entry_tags_lower for t in tags):
                    continue

            # Keyword search across multiple fields
            searchable = " ".join(
                filter(
                    None,
                    [
                        entry.corpus_id,
                        entry.title,
                        entry.domain,
                        entry.subdomain or "",
                        " ".join(entry.tags),
                    ],
                )
            ).lower()

            if query_lower in searchable:
                results.append(entry)

        return results

    def to_dict(self) -> dict:
        """Serialize to a dict suitable for YAML/JSON output."""
        return {
            "version": self.version,
            "generated_date": self.generated_date,
            "document_count": self.document_count,
            "documents": [d.to_dict() for d in self.documents],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "CorpusIndex":
        """Deserialize from a dict."""
        return cls(
            version=data["version"],
            generated_date=data["generated_date"],
            document_count=data["document_count"],
            documents=[
                CorpusIndexEntry.from_dict(d)
                for d in data.get("documents", [])
            ],
        )
