"""Stage 4: Intent Generator — Generate .intent.md files from enriched model."""
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

# Default goal type mapping for BPMN element types
_DEFAULT_GOAL_TYPES = {
    "task": "data_production",
    "userTask": "data_production",
    "serviceTask": "data_production",
    "businessRuleTask": "decision",
    "sendTask": "notification",
    "receiveTask": "data_production",
    "scriptTask": "data_production",
    "manualTask": "data_production",
    "callActivity": "orchestration",
    "subProcess": "orchestration",
    "exclusiveGateway": "decision",
    "inclusiveGateway": "decision",
    "parallelGateway": "orchestration",
    "eventBasedGateway": "decision",
    "startEvent": "state_transition",
    "endEvent": "state_transition",
    "intermediateCatchEvent": "state_transition",
    "intermediateThrowEvent": "notification",
    "boundaryEvent": "state_transition",
}

# Forbidden actions that must always be present
FORBIDDEN_ACTIONS = [
    "browser_automation",
    "screen_scraping",
    "ui_click",
    "rpa_style_macros",
]


def run_intent_generator(
    enriched: EnrichedModel,
    output_dir: Path,
    config: dict,
    llm_provider=None,
) -> list[Path]:
    """Generate intent spec files for all eligible nodes.
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
        if not elem_mapping.get("generates_intent", True):
            continue

        enrichment = enriched.get_enrichment(node.id)

        # Generate ID (must match capsule stem)
        category = _derive_category(node.name or node.id)
        seq_key = f"{id_prefix}-{category}"
        seq_counter[seq_key] = seq_counter.get(seq_key, 0) + 1
        seq = f"{seq_counter[seq_key]:03d}"

        capsule_id = f"CAP-{id_prefix}-{category}-{seq}"
        intent_id = f"INT-{id_prefix}-{category}-{seq}"
        contract_id = f"ICT-{id_prefix}-{category}-{seq}"

        # Determine goal type from mapping or defaults
        goal_type = (
            elem_mapping.get("default_goal_type")
            or node.attributes.get("default_goal_type")
            or _DEFAULT_GOAL_TYPES.get(node.element_type, "data_production")
        )

        # Derive goal statement
        task_name = node.name or node.id
        goal = f"Produce the required output for '{task_name}'"

        # Build inputs from data associations and predecessors
        inputs = _derive_inputs(node, enriched)
        outputs = _derive_outputs(node, enriched)

        # Read the capsule if it exists to inform the intent
        slug = task_name.lower().replace(" ", "-").replace("_", "-")
        slug = re.sub(r'[^a-z0-9-]', '', slug)
        triple_type = elem_mapping.get("triple_type", "standard")
        if triple_type == "decision":
            capsule_dir = output_dir.parent / "decisions" / slug
        else:
            capsule_dir = output_dir / slug

        capsule_content = ""
        capsule_path = capsule_dir / f"{slug}.cap.md"
        if capsule_path.exists():
            _, capsule_content = frontmatter_mod.read_frontmatter_file(capsule_path)

        # Build frontmatter
        fm = {
            "intent_id": intent_id,
            "capsule_id": capsule_id,
            "contract_ref": contract_id,
            "bpmn_task_id": node.id,
            "version": "1.0",
            "status": "draft",
            "mda_layer": "PIM",
            "goal": goal,
            "goal_type": goal_type,
            "generated_date": datetime.utcnow().isoformat(),
            "generated_by": "mda-cli",
            "last_modified": datetime.utcnow().isoformat(),
            "last_modified_by": "mda-cli",
            "inputs": inputs,
            "outputs": outputs,
            "preconditions": [f"Predecessor tasks for '{task_name}' have completed successfully"],
            "postconditions": [f"'{task_name}' output produced and validated"],
            "failure_modes": [
                {"mode": "input_validation_error", "detection": "Schema validation fails on input data", "action": "reject_with_details"},
                {"mode": "timeout", "detection": "Processing exceeds SLA threshold", "action": "escalate"},
            ],
            "execution_hints": {
                "preferred_agent": None,
                "tool_access": ["api_call", "data_query", "document_read"],
                "forbidden_actions": list(FORBIDDEN_ACTIONS),
            },
            "decision_rules": [],
            "regulatory_refs": [],
            "gaps": [],
            "tags": [],
        }

        # Add corpus refs from enrichment
        if enrichment and enrichment.procedure.found:
            fm["corpus_refs"] = [
                {"corpus_id": m.corpus_id, "section": "Intent", "match_confidence": m.match_confidence}
                for m in enrichment.procedure.corpus_refs[:3]
            ]

        # Add decision rules from enrichment
        if enrichment and enrichment.decision_rules and enrichment.decision_rules.defined:
            fm["decision_rules"] = enrichment.decision_rules.conditions

        # Add regulatory refs
        if enrichment and enrichment.regulatory.applicable:
            fm["regulatory_refs"] = [m.corpus_id for m in enrichment.regulatory.corpus_refs[:3]]

        # Add gaps
        node_gaps = [g for g in enriched.gaps if g.node_id == node.id]
        fm["gaps"] = [{"type": g.gap_type.value, "description": g.description, "severity": g.severity.value} for g in node_gaps]

        # Generate body
        if llm_provider and capsule_content:
            body = _generate_body_with_llm(node, fm, capsule_content, llm_provider)
        else:
            body = _generate_template_body(node, fm)

        # Write file
        capsule_dir.mkdir(parents=True, exist_ok=True)
        file_path = capsule_dir / f"{slug}.intent.md"
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


def _derive_inputs(node, enriched: EnrichedModel) -> list[dict]:
    """Derive intent inputs from data associations and predecessor outputs."""
    inputs = []
    parsed = enriched.parsed_model

    # From data associations pointing into this node
    for da in parsed.data_associations:
        if da.target_ref == node.id:
            # Find the data object
            data_obj = None
            for do in parsed.data_objects:
                if do.id == da.source_ref:
                    data_obj = do
                    break
            name = data_obj.name if data_obj and data_obj.name else da.source_ref
            inputs.append({
                "name": name,
                "source": f"data_object:{da.source_ref}",
                "schema_ref": None,
                "required": True,
            })

    # From predecessor outputs (inferred)
    predecessors = parsed.get_predecessors(node.id)
    for pred in predecessors:
        pred_name = pred.name or pred.id
        inputs.append({
            "name": f"{pred_name}_output",
            "source": f"predecessor:{pred.id}",
            "schema_ref": None,
            "required": True,
        })

    # If no inputs found, add a placeholder
    if not inputs:
        inputs.append({
            "name": "process_context",
            "source": "pipeline",
            "schema_ref": None,
            "required": True,
        })

    return inputs


def _derive_outputs(node, enriched: EnrichedModel) -> list[dict]:
    """Derive intent outputs from data associations and task type."""
    outputs = []
    parsed = enriched.parsed_model

    # From data associations going out of this node
    for da in parsed.data_associations:
        if da.source_ref == node.id:
            data_obj = None
            for do in parsed.data_objects:
                if do.id == da.target_ref:
                    data_obj = do
                    break
            name = data_obj.name if data_obj and data_obj.name else da.target_ref
            outputs.append({
                "name": name,
                "type": "data_object",
                "sink": f"data_object:{da.target_ref}",
                "invariants": [f"{name} must be non-null", f"{name} must pass schema validation"],
            })

    # Default output based on task
    if not outputs:
        task_name = node.name or node.id
        outputs.append({
            "name": f"{task_name}_result",
            "type": "structured_data",
            "sink": "next_task",
            "invariants": [f"{task_name}_result must contain status field"],
        })

    return outputs


def _generate_template_body(node, frontmatter: dict) -> str:
    """Generate a template body without LLM (--skip-llm mode)."""
    name = node.name or node.id
    body = f"# {name} -- Intent Specification\n\n"
    body += "## Outcome Statement\n\n<!-- TODO: Describe the required outcome (WHAT, not HOW) -->\n\n"
    body += "## Outcome Contract\n\n<!-- TODO: Define when this intent is satisfied -->\n\n"
    body += "## Reasoning Guidance\n\n<!-- TODO: Add numbered reasoning steps for the agent -->\n\n"
    body += "## Anti-Patterns\n\n"
    body += "- **NEVER** use browser automation to satisfy this intent\n"
    body += "- **NEVER** scrape screens or parse rendered HTML\n"
    body += "- **NEVER** click UI elements or interact with GUIs\n"
    body += "- **NEVER** use RPA-style macros or record-and-playback\n\n"
    body += f"## Paired Capsule\n\n- Capsule ID: `{frontmatter.get('capsule_id', 'TBD')}`\n\n"
    body += f"## Paired Integration Contract\n\n- Contract ID: `{frontmatter.get('contract_ref', 'TBD')}`\n\n"
    body += "## Notes\n\n<!-- Generated by mda-cli without LLM. Fill in manually or re-run with LLM. -->\n"
    return body


def _generate_body_with_llm(node, frontmatter, capsule_content, llm_provider) -> str:
    """Generate body using LLM with capsule content."""
    from llm.prompts.intent import INTENT_SYSTEM, build_intent_body_prompt

    node_context = {
        "name": node.name or node.id,
        "element_type": node.element_type,
        "default_goal_type": frontmatter.get("goal_type", "data_production"),
    }

    prompt = build_intent_body_prompt(node_context, frontmatter)
    response = llm_provider.complete(prompt, system_prompt=INTENT_SYSTEM, max_tokens=4096)
    return response.content
