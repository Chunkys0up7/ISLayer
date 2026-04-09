"""Stage 5: Contract Generator — Generate .contract.md files from enriched model."""
from pathlib import Path
from datetime import datetime
from typing import Optional
import re
import json

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import importlib.util
def _load_io(name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "mda_io", f"{name}.py"))
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod); return mod
frontmatter_mod = _load_io("frontmatter")
yaml_io = _load_io("yaml_io")

from models.enriched import EnrichedModel
from models.bpmn import ParsedModel


def run_contract_generator(
    enriched: EnrichedModel,
    output_dir: Path,
    config: dict,
    llm_provider=None,
) -> list[Path]:
    """Generate integration contract files for all eligible nodes.
    Returns list of created file paths.
    """
    created = []
    id_prefix = config.get("naming", {}).get("id_prefix", "XX")
    process_name = config.get("process", {}).get("name", "Unknown Process")
    process_id = config.get("process", {}).get("id", "Unknown")

    # Load ontology for element mapping
    ontology_dir = Path(config.get("pipeline", {}).get("ontology", "../../ontology/"))
    mapping = {}
    mapping_path = ontology_dir / "bpmn-element-mapping.yaml"
    if mapping_path.exists():
        mapping_data = yaml_io.read_yaml(mapping_path)
        for entry in mapping_data.get("mappings", []):
            mapping[entry.get("bpmn_element", "")] = entry

    seq_counter = {}

    for node in enriched.parsed_model.nodes:
        elem_mapping = mapping.get(node.element_type, {})
        if not elem_mapping.get("generates_contract", True):
            continue

        enrichment = enriched.get_enrichment(node.id)

        # Generate ID (must match capsule/intent stem)
        category = _derive_category(node.name or node.id)
        seq_key = f"{id_prefix}-{category}"
        seq_counter[seq_key] = seq_counter.get(seq_key, 0) + 1
        seq = f"{seq_counter[seq_key]:03d}"

        intent_id = f"INT-{id_prefix}-{category}-{seq}"
        contract_id = f"ICT-{id_prefix}-{category}-{seq}"

        task_name = node.name or node.id

        # Resolve the triple directory
        slug = task_name.lower().replace(" ", "-").replace("_", "-")
        slug = re.sub(r'[^a-z0-9-]', '', slug)
        triple_type = elem_mapping.get("triple_type", "standard")
        if triple_type == "decision":
            triple_dir = output_dir.parent / "decisions" / slug
        else:
            triple_dir = output_dir / slug

        # Read the intent if it exists to inform the contract
        intent_fm = {}
        intent_path = triple_dir / f"{slug}.intent.md"
        if intent_path.exists():
            intent_fm, _ = frontmatter_mod.read_frontmatter_file(intent_path)

        # Map intent inputs to sources
        sources = _derive_sources(node, enrichment, intent_fm)
        sinks = _derive_sinks(node, enrichment, intent_fm)
        events = _derive_events(node, task_name, process_id)

        # Build frontmatter
        fm = {
            "contract_id": contract_id,
            "intent_id": intent_id,
            "version": "1.0",
            "status": "draft",
            "mda_layer": "PSM",
            "binding_status": "unbound",
            "generated_date": datetime.utcnow().isoformat(),
            "generated_by": "mda-cli",
            "last_modified": datetime.utcnow().isoformat(),
            "last_modified_by": "mda-cli",
            "sources": sources,
            "sinks": sinks,
            "events_published": events,
            "events_consumed": [],
            "audit": {
                "record_type": f"{slug}_audit",
                "retention_years": 7,
                "fields_required": ["timestamp", "actor", "action", "result"],
                "sink": "audit_log",
            },
            "sla_ms": 30000,
            "retry_policy": {
                "max_retries": 3,
                "backoff": "exponential",
                "initial_delay_ms": 1000,
            },
            "idempotency": {
                "strategy": "request_id",
                "ttl_hours": 24,
            },
            "tags": [],
        }

        # Determine binding status
        all_endpoints = [s.get("endpoint", "") for s in sources + sinks]
        bound_count = sum(1 for ep in all_endpoints if ep and not ep.startswith("TBD:"))
        total = len(all_endpoints) if all_endpoints else 1
        if bound_count == total and total > 0:
            fm["binding_status"] = "bound"
        elif bound_count > 0:
            fm["binding_status"] = "partial"
        else:
            fm["binding_status"] = "unbound"

        # Generate body
        if llm_provider and intent_fm:
            body = _generate_body_with_llm(node, fm, intent_fm, enrichment, llm_provider)
        else:
            body = _generate_template_body(node, fm)

        # Write file
        triple_dir.mkdir(parents=True, exist_ok=True)
        file_path = triple_dir / f"{slug}.contract.md"
        frontmatter_mod.write_frontmatter_file(file_path, fm, body)
        created.append(file_path)

    return created


def _derive_category(name: str) -> str:
    """Derive a 3-letter category code from a task name."""
    mappings = {
        "application": "APP", "receive": "RCV", "verify": "VER", "credit": "CRC",
        "identity": "IDV", "income": "INC", "dti": "DTI", "debt": "DTI",
        "document": "DOC", "package": "PKG", "submit": "SUB", "underwriting": "UND",
        "appraisal": "APR", "order": "ORD", "review": "MRV", "validate": "VAL",
        "classify": "CLS", "calculate": "QAL", "emit": "NTF", "notify": "NTF",
        "request": "REQ", "assess": "ASV", "eligible": "DEC", "threshold": "DEC",
        "complete": "CMP", "timeout": "TMO", "reject": "REJ", "flag": "FLG",
    }
    name_lower = name.lower()
    for keyword, code in mappings.items():
        if keyword in name_lower:
            return code
    consonants = [c.upper() for c in name_lower if c.isalpha() and c not in "aeiou"]
    return "".join(consonants[:3]) if len(consonants) >= 3 else name[:3].upper()


def _derive_sources(node, enrichment, intent_fm: dict) -> list[dict]:
    """Map intent inputs to integration sources."""
    sources = []
    intent_inputs = intent_fm.get("inputs", [])

    for inp in intent_inputs:
        if isinstance(inp, dict):
            name = inp.get("name", "unknown")
            source_ref = inp.get("source", "")

            # Determine protocol based on source type
            if "predecessor" in source_ref:
                protocol = "internal"
                endpoint = f"TBD:pipeline/{source_ref}"
            elif "data_object" in source_ref:
                protocol = "rest"
                endpoint = f"TBD:GET /api/v2/{name.lower().replace('_', '-')}"
            else:
                protocol = "rest"
                endpoint = f"TBD:GET /api/v2/{name.lower().replace('_', '-')}"

            # Check if enrichment has a system binding
            if enrichment and enrichment.integration.has_binding:
                system = enrichment.integration.system_name or "unknown"
                endpoint = f"TBD:{system}/api/v2/{name.lower().replace('_', '-')}"

            sources.append({
                "name": name,
                "protocol": protocol,
                "endpoint": endpoint,
                "auth": "bearer_token",
                "schema_ref": inp.get("schema_ref"),
                "sla_ms": 5000,
            })

    if not sources:
        sources.append({
            "name": "process_context",
            "protocol": "internal",
            "endpoint": "TBD:pipeline/context",
            "auth": None,
            "schema_ref": None,
            "sla_ms": 1000,
        })

    return sources


def _derive_sinks(node, enrichment, intent_fm: dict) -> list[dict]:
    """Map intent outputs to integration sinks."""
    sinks = []
    intent_outputs = intent_fm.get("outputs", [])

    for out in intent_outputs:
        if isinstance(out, dict):
            name = out.get("name", "unknown")
            sink_ref = out.get("sink", "")

            if "data_object" in sink_ref:
                protocol = "rest"
                endpoint = f"TBD:PUT /api/v2/{name.lower().replace('_', '-')}"
            elif sink_ref == "next_task":
                protocol = "internal"
                endpoint = f"TBD:pipeline/output/{name.lower().replace('_', '-')}"
            else:
                protocol = "rest"
                endpoint = f"TBD:POST /api/v2/{name.lower().replace('_', '-')}"

            if enrichment and enrichment.integration.has_binding:
                system = enrichment.integration.system_name or "unknown"
                endpoint = f"TBD:{system}/api/v2/{name.lower().replace('_', '-')}"

            sinks.append({
                "name": name,
                "protocol": protocol,
                "endpoint": endpoint,
                "auth": "bearer_token",
                "schema_ref": None,
                "sla_ms": 5000,
                "idempotency_key": f"{name}_request_id",
            })

    if not sinks:
        task_name = (node.name or node.id).lower().replace(" ", "_")
        sinks.append({
            "name": f"{task_name}_result",
            "protocol": "internal",
            "endpoint": f"TBD:pipeline/output/{task_name}",
            "auth": None,
            "schema_ref": None,
            "sla_ms": 5000,
            "idempotency_key": None,
        })

    return sinks


def _derive_events(node, task_name: str, process_id: str) -> list[dict]:
    """Generate completion/notification events."""
    slug = task_name.lower().replace(" ", "_").replace("-", "_")
    return [
        {
            "topic": f"{process_id}.{slug}.completed",
            "schema_ref": None,
            "delivery": "at_least_once",
            "key_field": "correlation_id",
        }
    ]


def _generate_template_body(node, frontmatter: dict) -> str:
    """Generate a template body without LLM (--skip-llm mode)."""
    name = node.name or node.id
    body = f"# {name} -- Integration Contract\n\n"
    body += "## Binding Rationale\n\n<!-- TODO: Explain why these systems/APIs were chosen -->\n\n"
    body += "## Source Bindings\n\n"

    for src in frontmatter.get("sources", []):
        sname = src.get("name", "unknown")
        body += f"### {sname}\n\n"
        body += f"- Protocol: `{src.get('protocol', 'TBD')}`\n"
        body += f"- Endpoint: `{src.get('endpoint', 'TBD')}`\n"
        body += f"- Auth: `{src.get('auth', 'TBD')}`\n"
        body += f"- SLA: {src.get('sla_ms', 'TBD')}ms\n\n"

    body += "## Sink Bindings\n\n"
    for snk in frontmatter.get("sinks", []):
        sname = snk.get("name", "unknown")
        body += f"### {sname}\n\n"
        body += f"- Protocol: `{snk.get('protocol', 'TBD')}`\n"
        body += f"- Endpoint: `{snk.get('endpoint', 'TBD')}`\n"
        body += f"- Auth: `{snk.get('auth', 'TBD')}`\n"
        body += f"- SLA: {snk.get('sla_ms', 'TBD')}ms\n\n"

    body += "## Change Protocol\n\n"
    body += "- **Non-breaking**: Adding optional fields, adding new event topics\n"
    body += "- **Breaking**: Removing fields, changing endpoint paths, altering auth schemes\n"
    body += "- Breaking changes require version bump and downstream notification\n\n"

    body += "## Decommissioning\n\n"
    body += "<!-- TODO: Define what happens when a source/sink is retired -->\n\n"

    body += "## Notes\n\n<!-- Generated by mda-cli without LLM. Fill in manually or re-run with LLM. -->\n"
    return body


def _generate_body_with_llm(node, contract_fm, intent_fm, enrichment, llm_provider) -> str:
    """Generate body using LLM with intent content."""
    from llm.prompts.contract import CONTRACT_SYSTEM, build_contract_body_prompt

    prompt = build_contract_body_prompt(contract_fm)
    response = llm_provider.complete(prompt, system_prompt=CONTRACT_SYSTEM, max_tokens=4096)
    return response.content
