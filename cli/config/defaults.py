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
