"""Stage 3: Capsule Generator — Generate .cap.md files from enriched model.

Uses a two-pass approach:
  Pass 1: Assign capsule IDs to all eligible nodes (build the ID registry)
  Pass 2: Generate capsule files with correct predecessor/successor references

Grounding improvements:
  - Section-level corpus extraction (no truncation)
  - Job aid injection as structured decision tables
  - Post-generation verification of corpus citations
  - Provenance chain in frontmatter
"""
from pathlib import Path
from datetime import datetime
from typing import Optional
import re

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


def run_capsule_generator(
    enriched: EnrichedModel,
    output_dir: Path,
    config: dict,
    corpus_dir: Optional[Path] = None,
    llm_provider=None,
) -> list[Path]:
    """Generate capsule files for all eligible nodes.

    Two-pass approach:
      Pass 1: Build a registry mapping BPMN node ID -> capsule/intent/contract IDs
      Pass 2: Generate capsule files using the registry for predecessor/successor refs

    Returns list of created file paths.
    Also attaches the id_registry to the enriched model for use by stages 4 and 5.
    """
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

    # ================================================================
    # PASS 1: Assign IDs to all eligible nodes (build the ID registry)
    # ================================================================
    id_registry = {}
    seq_counter = {}

    for node in enriched.parsed_model.nodes:
        elem_mapping = mapping.get(node.element_type, {})
        if not elem_mapping.get("generates_capsule", True):
            continue

        category = _derive_category(node.name or node.id)
        seq_key = f"{id_prefix}-{category}"
        seq_counter[seq_key] = seq_counter.get(seq_key, 0) + 1
        seq = f"{seq_counter[seq_key]:03d}"

        capsule_id = f"CAP-{id_prefix}-{category}-{seq}"
        intent_id = f"INT-{id_prefix}-{category}-{seq}"
        contract_id = f"ICT-{id_prefix}-{category}-{seq}"

        slug = (node.name or node.id).lower().replace(" ", "-").replace("_", "-")
        slug = re.sub(r'[^a-z0-9-]', '', slug)

        triple_type = elem_mapping.get("triple_type", "standard")

        id_registry[node.id] = {
            "capsule_id": capsule_id,
            "intent_id": intent_id,
            "contract_id": contract_id,
            "slug": slug,
            "triple_type": triple_type,
            "generates_intent": elem_mapping.get("generates_intent", True),
            "generates_contract": elem_mapping.get("generates_contract", True),
        }

    # Attach registry to enriched model for use by stages 4, 5, and graph builder
    enriched.id_registry = id_registry

    # ================================================================
    # PASS 2: Generate capsule files with correct cross-references
    # ================================================================
    created = []

    for node in enriched.parsed_model.nodes:
        if node.id not in id_registry:
            continue

        reg = id_registry[node.id]
        enrichment = enriched.get_enrichment(node.id)

        # Build predecessor/successor IDs from the registry
        predecessor_ids = []
        for pred in enriched.parsed_model.get_predecessors(node.id):
            if pred.id in id_registry:
                predecessor_ids.append(id_registry[pred.id]["capsule_id"])

        successor_ids = []
        for succ in enriched.parsed_model.get_successors(node.id):
            if succ.id in id_registry:
                successor_ids.append(id_registry[succ.id]["capsule_id"])

        # Build exception IDs (boundary events attached to this node)
        exception_ids = []
        for be_id in node.boundary_event_ids:
            if be_id in id_registry:
                exception_ids.append(id_registry[be_id]["capsule_id"])

        # Build provenance chain for corpus refs
        corpus_refs_with_provenance = []
        if enrichment and enrichment.procedure.found:
            for m in enrichment.procedure.corpus_refs[:3]:
                corpus_refs_with_provenance.append({
                    "corpus_id": m.corpus_id,
                    "section": "Procedure",
                    "match_confidence": m.match_confidence,
                    "match_method": m.match_method,
                    "match_score": m.match_score,
                })

        # Build regulatory refs with provenance
        regulation_refs = []
        policy_refs = []
        if enrichment and enrichment.regulatory.applicable:
            for m in enrichment.regulatory.corpus_refs:
                corpus_refs_with_provenance.append({
                    "corpus_id": m.corpus_id,
                    "section": "Regulatory",
                    "match_confidence": m.match_confidence,
                    "match_method": m.match_method,
                    "match_score": m.match_score,
                })

        # Job aid references
        jobaid_refs = []
        if enrichment and hasattr(enrichment, 'jobaid_refs') and enrichment.jobaid_refs:
            for ja in enrichment.jobaid_refs:
                jobaid_refs.append({
                    "jobaid_id": ja.get("jobaid_id", ""),
                    "title": ja.get("title", ""),
                    "dimensions": ja.get("dimensions", []),
                    "rules_count": ja.get("rules_count", 0),
                })

        # Build frontmatter
        fm = {
            "capsule_id": reg["capsule_id"],
            "bpmn_task_id": node.id,
            "bpmn_task_name": node.name or node.id,
            "bpmn_task_type": node.element_type,
            "process_id": process_id,
            "process_name": process_name,
            "version": "1.0",
            "status": "draft",
            "generated_from": enriched.parsed_model.source_file or "unknown",
            "generated_date": datetime.utcnow().isoformat(),
            "generated_by": "mda-cli",
            "last_modified": datetime.utcnow().isoformat(),
            "last_modified_by": "mda-cli",
            "owner_role": enrichment.ownership.owner_role if enrichment and enrichment.ownership.resolved else None,
            "owner_team": enrichment.ownership.owner_team if enrichment and enrichment.ownership.resolved else None,
            "reviewers": [],
            "domain": config.get("process", {}).get("domain", ""),
            "subdomain": "",
            "regulation_refs": regulation_refs,
            "policy_refs": policy_refs,
            "intent_id": reg["intent_id"],
            "contract_id": reg["contract_id"],
            "parent_capsule_id": None,
            "predecessor_ids": predecessor_ids,
            "successor_ids": successor_ids,
            "exception_ids": exception_ids,
            "corpus_refs": corpus_refs_with_provenance,
            "jobaid_refs": jobaid_refs,
            "gaps": [],
            "grounding_verification": None,
        }

        # Add gaps from enrichment
        node_gaps = [g for g in enriched.gaps if g.node_id == node.id]
        fm["gaps"] = [{"type": g.gap_type.value, "description": g.description, "severity": g.severity.value} for g in node_gaps]

        # Generate body
        if llm_provider and corpus_dir:
            body, verification = _generate_body_with_llm(node, enrichment, corpus_dir, llm_provider, fm)
            fm["grounding_verification"] = verification
        else:
            body = _generate_template_body(node, enrichment, fm)

        # Determine output subdirectory
        if reg["triple_type"] == "decision":
            subdir = output_dir.parent / "decisions" / reg["slug"]
        else:
            subdir = output_dir / reg["slug"]
        subdir.mkdir(parents=True, exist_ok=True)

        file_path = subdir / f"{reg['slug']}.cap.md"
        frontmatter_mod.write_frontmatter_file(file_path, fm, body)
        created.append(file_path)

    return created


def get_id_registry(enriched: EnrichedModel) -> dict:
    """Get the ID registry from an enriched model (set during capsule generation)."""
    return getattr(enriched, 'id_registry', {})


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
        "start": "STA", "end": "END", "w-2": "W2V", "self-employ": "SEI",
        "variance": "VAR",
    }
    name_lower = name.lower()
    for keyword, code in mappings.items():
        if keyword in name_lower:
            return code
    consonants = [c.upper() for c in name_lower if c.isalpha() and c not in "aeiou"]
    return "".join(consonants[:3]) if len(consonants) >= 3 else name[:3].upper()


def _generate_template_body(node, enrichment, frontmatter: dict) -> str:
    """Generate a template body without LLM (--skip-llm mode).

    Now includes job aid content if available (deterministic extraction).
    """
    name = node.name or node.id
    body = f"# {name}\n\n"
    body += "## Purpose\n\n<!-- TODO: Describe the purpose of this task -->\n\n"
    body += "## Procedure\n\n<!-- TODO: Add step-by-step procedure -->\n\n"

    # Inject job aid as decision parameters if available
    if enrichment and hasattr(enrichment, 'jobaid_refs') and enrichment.jobaid_refs:
        body += _format_jobaid_section(enrichment.jobaid_refs)

    body += "## Business Rules\n\n<!-- TODO: Add business rules -->\n\n"
    body += "## Inputs Required\n\n| Input | Source | Description |\n|-------|--------|-------------|\n| <!-- TODO --> | | |\n\n"
    body += "## Outputs Produced\n\n| Output | Destination | Description |\n|--------|-------------|-------------|\n| <!-- TODO --> | | |\n\n"
    body += "## Exception Handling\n\n<!-- TODO: Add exception handling -->\n\n"
    body += "## Regulatory Context\n\n<!-- TODO: Add regulatory context -->\n\n"
    body += "## Notes\n\n<!-- Generated by mda-cli without LLM. Fill in manually or re-run with LLM. -->\n"
    return body


def _generate_body_with_llm(node, enrichment, corpus_dir, llm_provider, frontmatter) -> tuple:
    """Generate body using LLM with section-level extracted corpus content.

    Returns (body_text, verification_result) tuple.
    """
    from pipeline.stage2_enricher import extract_grounded_content, verify_grounding
    from llm.prompts.capsule import CAPSULE_SYSTEM, build_capsule_body_prompt

    # Step 1: Extract section-level content from corpus (NO truncation)
    grounded_content = {}
    provided_corpus_ids = []
    if enrichment:
        grounded_content = extract_grounded_content(corpus_dir, enrichment, node.element_type)
        # Collect all corpus IDs that were provided to the LLM
        for section_items in grounded_content.values():
            for item in section_items:
                if item["corpus_id"] not in provided_corpus_ids:
                    provided_corpus_ids.append(item["corpus_id"])

    # Step 2: Format job aid content (deterministic — no LLM involvement)
    jobaid_content = ""
    if enrichment and hasattr(enrichment, 'jobaid_refs') and enrichment.jobaid_refs:
        jobaid_content = _format_jobaid_section(enrichment.jobaid_refs)

    # Step 3: Build enrichment summary
    enrichment_summary = {
        "procedure_found": enrichment.procedure.found if enrichment else False,
        "procedure_match_count": len(enrichment.procedure.corpus_refs) if enrichment and enrichment.procedure.found else 0,
        "regulatory_applicable": enrichment.regulatory.applicable if enrichment else False,
        "has_jobaid": bool(jobaid_content),
    }

    # Step 4: Build node context
    node_context = {
        "name": node.name or node.id,
        "element_type": node.element_type,
        "lane_name": node.lane_name,
        "predecessor_names": [],
        "successor_names": [],
    }

    # Step 5: Call LLM with extraction-based prompt
    prompt = build_capsule_body_prompt(node_context, grounded_content, enrichment_summary, jobaid_content)
    response = llm_provider.complete(prompt, system_prompt=CAPSULE_SYSTEM, max_tokens=4096, temperature=0.15)

    # Step 6: Verify grounding
    verification = verify_grounding(response.content, grounded_content, provided_corpus_ids)

    # Step 7: If verification fails and we have content, retry with stricter prompt
    if not verification["valid"] and provided_corpus_ids:
        # Retry once with explicit warning
        retry_prompt = (
            "GROUNDING VERIFICATION FAILED on previous attempt.\n"
            f"Uncited sections: {verification['uncited_sections']}\n"
            f"Invalid citations: {verification['invalid_citations']}\n\n"
            "You MUST cite a (CORPUS-ID) for every factual statement.\n"
            "Available corpus IDs: " + ", ".join(provided_corpus_ids) + "\n\n"
            + prompt
        )
        response = llm_provider.complete(retry_prompt, system_prompt=CAPSULE_SYSTEM, max_tokens=4096, temperature=0.1)
        verification = verify_grounding(response.content, grounded_content, provided_corpus_ids)

    return response.content, verification


def _format_jobaid_section(jobaid_refs: list) -> str:
    """Format job aid data as a deterministic markdown section.

    This is pure extraction from job aid YAML — zero LLM involvement.
    """
    if not jobaid_refs:
        return ""

    sections = []
    for ja in jobaid_refs:
        ja_id = ja.get("jobaid_id", "unknown")
        title = ja.get("title", "")
        dims = ja.get("dimensions", [])
        action_fields = ja.get("action_fields", [])
        rules_count = ja.get("rules_count", 0)
        default_action = ja.get("default_action")
        precedence = ja.get("precedence", "first_match")

        section = f"## Decision Parameters (Job Aid: {ja_id})\n\n"
        if title:
            section += f"**Title**: {title}\n\n"

        # Dimensions table
        if dims:
            section += "### Dimensions\n\n"
            section += "| Dimension | Required at Resolution |\n"
            section += "|-----------|----------------------|\n"
            for d in dims:
                if isinstance(d, dict):
                    section += f"| {d.get('name', '')} | {d.get('required_at_resolution', True)} |\n"
                else:
                    section += f"| {d} | Yes |\n"
            section += "\n"

        # Action fields
        if action_fields:
            section += "### Action Fields\n\n"
            section += "| Field | Type |\n"
            section += "|-------|------|\n"
            for af in action_fields:
                if isinstance(af, dict):
                    section += f"| {af.get('name', '')} | {af.get('type', 'string')} |\n"
                else:
                    section += f"| {af} | string |\n"
            section += "\n"

        section += f"**Total Rules**: {rules_count}\n"
        section += f"**Precedence**: {precedence}\n"

        if default_action:
            section += f"\n**Default Action**: {default_action}\n"

        # Load and render full decision table if path available
        ja_path = ja.get("path")
        if ja_path:
            try:
                ja_data = yaml_io.read_yaml(Path(ja_path))
                if ja_data and "rules" in ja_data:
                    rules = ja_data["rules"]
                    if rules:
                        section += "\n### Decision Table\n\n"
                        # Build header from first rule
                        cond_keys = list(rules[0].get("conditions", {}).keys())
                        action_keys = list(rules[0].get("action", {}).keys())
                        header = "| " + " | ".join(cond_keys) + " | " + " | ".join(f"-> {k}" for k in action_keys) + " |"
                        separator = "| " + " | ".join("---" for _ in cond_keys + action_keys) + " |"
                        section += header + "\n" + separator + "\n"
                        for rule in rules[:50]:  # Cap at 50 rules for readability
                            conds = rule.get("conditions", {})
                            acts = rule.get("action", {})
                            row = "| " + " | ".join(str(conds.get(k, "*")) for k in cond_keys)
                            row += " | " + " | ".join(str(acts.get(k, "")) for k in action_keys) + " |"
                            section += row + "\n"
                        if len(rules) > 50:
                            section += f"\n*... and {len(rules) - 50} more rules (see {ja_id})*\n"
                        section += "\n"
            except Exception:
                pass  # Job aid will still be referenced in frontmatter

        sections.append(section)

    return "\n".join(sections)


def _find_corpus_doc(corpus_dir: Path, corpus_id: str) -> Optional[Path]:
    """Find a corpus document file by its ID."""
    index_path = corpus_dir / "corpus.config.yaml"
    if index_path.exists():
        index = yaml_io.read_yaml(index_path)
        for doc in index.get("documents", []):
            if doc.get("corpus_id") == corpus_id:
                return corpus_dir / doc.get("path", "")
    for f in corpus_dir.rglob("*.corpus.md"):
        fm, _ = frontmatter_mod.read_frontmatter_file(f)
        if fm.get("corpus_id") == corpus_id:
            return f
    return None
