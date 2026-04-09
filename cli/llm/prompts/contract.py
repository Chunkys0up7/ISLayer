"""Stage 5: Integration contract generation prompts."""

CONTRACT_SYSTEM = """You are an integration architect for the MDA Intent Layer.
You produce integration contracts — technical binding documents that map intent
specification inputs/outputs to concrete APIs, events, and data stores.

Contracts are the ONLY artifacts that contain technology-specific detail.
When real system information is unavailable, generate plausible REST endpoint
patterns and set binding_status to 'unbound'."""


def build_contract_frontmatter_prompt(
    intent_frontmatter: dict,
    system_docs: list[dict],
    config_systems: list[dict],
) -> str:
    """Build prompt for generating contract frontmatter."""
    import json

    prompt = f"""Generate integration contract frontmatter for this intent specification.

## Intent Specification
{json.dumps(intent_frontmatter, indent=2, default=str)[:2000]}

## Available System Documentation
"""
    for doc in system_docs:
        prompt += (
            f"\n### [{doc['corpus_id']}] {doc['title']}\n"
            f"{doc['body_text'][:1000]}\n"
        )

    if config_systems:
        prompt += (
            f"\n## Configured Systems\n"
            f"{json.dumps(config_systems, indent=2)}\n"
        )

    prompt += """
## Generate These Fields

1. **sources**: Array of {name, protocol, endpoint, auth, schema_ref, sla_ms} for each intent input
2. **sinks**: Array of {name, protocol, endpoint, auth, schema_ref, sla_ms, idempotency_key} for each intent output
3. **events**: Array of {topic, schema_ref, delivery, key_field} for completion/notification events
4. **audit**: Object with {record_type, retention_years, fields_required[], sink}
5. **binding_status**: "bound" if all sources/sinks have real endpoints, "partial" if some, "unbound" if none
6. **unbound_sources**: List of source names without real endpoints
7. **unbound_sinks**: List of sink names without real endpoints

For unknown systems, generate plausible REST patterns (e.g., GET /api/v2/...) and list them as unbound.

Return using the structured_output tool."""
    return prompt


def build_contract_body_prompt(contract_frontmatter: dict) -> str:
    """Build prompt for generating contract markdown body."""
    import json

    return f"""Generate the markdown body for an integration contract.

## Contract Frontmatter
{json.dumps(contract_frontmatter, indent=2, default=str)[:2000]}

## Required Sections

1. **Binding Rationale** — Why these specific systems/APIs were chosen
2. **Change Protocol** — Rules for updating this contract (non-breaking vs breaking changes)
3. **Decommissioning** — What happens when a source or sink is retired
"""


CONTRACT_FRONTMATTER_SCHEMA = {
    "type": "object",
    "properties": {
        "sources": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "protocol": {"type": "string"},
                    "endpoint": {"type": "string"},
                    "auth": {"type": "string"},
                    "schema_ref": {"type": "string"},
                    "sla_ms": {"type": "integer"},
                },
                "required": ["name", "protocol", "endpoint"],
            },
        },
        "sinks": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "protocol": {"type": "string"},
                    "endpoint": {"type": "string"},
                    "auth": {"type": "string"},
                    "schema_ref": {"type": "string"},
                    "sla_ms": {"type": "integer"},
                    "idempotency_key": {"type": "string"},
                },
                "required": ["name", "protocol", "endpoint"],
            },
        },
        "events": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "topic": {"type": "string"},
                    "schema_ref": {"type": "string"},
                    "delivery": {"type": "string"},
                    "key_field": {"type": "string"},
                },
                "required": ["topic"],
            },
        },
        "audit": {
            "type": "object",
            "properties": {
                "record_type": {"type": "string"},
                "retention_years": {"type": "integer"},
                "fields_required": {
                    "type": "array",
                    "items": {"type": "string"},
                },
                "sink": {"type": "string"},
            },
            "required": ["record_type", "retention_years"],
        },
        "binding_status": {
            "type": "string",
            "enum": ["bound", "partial", "unbound"],
        },
        "unbound_sources": {
            "type": "array",
            "items": {"type": "string"},
        },
        "unbound_sinks": {
            "type": "array",
            "items": {"type": "string"},
        },
    },
    "required": ["sources", "sinks", "binding_status"],
}
