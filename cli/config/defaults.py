"""Default configuration values and path constants for the MDA Intent Layer CLI."""

from pathlib import Path

# Default config values used when no mda.config.yaml is found
DEFAULTS = {
    "mda": {"version": "1.0.0"},
    "paths": {
        "bpmn": "bpmn/",
        "triples": "triples/",
        "decisions": "decisions/",
        "graph": "graph/",
        "gaps": "gaps/",
        "audit": "audit/",
        "corpus": "../../corpus",
    },
    "llm": {
        "provider": "anthropic",
        "model": "claude-sonnet-4-20250514",
        "api_key_env": "ANTHROPIC_API_KEY",
        "temperature": 0.2,
        "max_tokens": 4096,
    },
    "pipeline": {
        "schemas": "../../schemas/",
        "ontology": "../../ontology/",
    },
    "corpus": {
        "source": "local",
        "local_path": "../../corpus",
        "s3": {
            "bucket": "",
            "prefix": "corpus/",
            "region": "us-east-1",
            "sync_to": ".corpus-cache/",
        },
    },
    "enrichment": {
        "match_threshold": 0.4,
        "high_confidence": 0.8,
        "medium_confidence": 0.5,
        "max_matches_per_type": 3,
        "disambiguation_band": 0.1,
        "weights": {
            "subdomain_match": 0.25,
            "tag_overlap_ratio": 0.20,
            "doc_type_relevance": 0.15,
            "role_match": 0.10,
            "data_object_match": 0.15,
            "related_corpus_bonus": 0.10,
            "goal_type_match": 0.05,
        },
        "doc_type_relevance_scores": {
            "procedure": 1.0,
            "rule": 0.9,
            "policy": 0.8,
            "regulation": 0.8,
            "data-dictionary": 0.7,
            "system": 0.6,
            "training": 0.4,
            "glossary": 0.3,
        },
    },
    "bitbucket": {
        "url": "",
        "project": "",
        "repo": "",
        "default_reviewers": [],
    },
    "defaults": {
        "status": "draft",
        "binding_status": "unbound",
        "audit_retention_years": 7,
    },
}

# Schema file names
SCHEMA_NAMES = {
    "capsule": "capsule.schema.json",
    "intent": "intent.schema.json",
    "contract": "contract.schema.json",
    "corpus_document": "corpus-document.schema.json",
    "triple_manifest": "triple-manifest.schema.json",
}

# Ontology file names
ONTOLOGY_NAMES = {
    "goal_types": "goal-types.yaml",
    "status_lifecycle": "status-lifecycle.yaml",
    "bpmn_element_mapping": "bpmn-element-mapping.yaml",
    "id_conventions": "id-conventions.yaml",
    "corpus_taxonomy": "corpus-taxonomy.yaml",
}
