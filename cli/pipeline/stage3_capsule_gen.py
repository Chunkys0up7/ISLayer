"""Stage 3: Capsule Generator — Generate .cap.md files from enriched model.

Uses a two-pass approach:
  Pass 1: Assign capsule IDs to all eligible nodes (build the ID registry)
  Pass 2: Generate capsule files with correct predecessor/successor references
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
      Pass 1: Build a registry mapping BPMN node ID → capsule/intent/contract IDs
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
    id_registry = {}  # BPMN node ID → {"capsule_id", "intent_id", "contract_id", "slug", "triple_type"}
    seq_counter = {}  # category key → next sequence number

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
            "regulation_refs": [],
            "policy_refs": [],
            "intent_id": reg["intent_id"],
            "contract_id": reg["contract_id"],
            "parent_capsule_id": None,
            "predecessor_ids": predecessor_ids,
            "successor_ids": successor_ids,
            "exception_ids": exception_ids,
            "gaps": [],
        }

        # Add corpus refs if available
        if enrichment and enrichment.procedure.found:
            fm["corpus_refs"] = [
                {"corpus_id": m.corpus_id, "section": "Procedure", "match_confidence": m.match_confidence}
                for m in enrichment.procedure.corpus_refs[:3]
            ]

        # Add gaps from enrichment
        node_gaps = [g for g in enriched.gaps if g.node_id == node.id]
        fm["gaps"] = [{"type": g.gap_type.value, "description": g.description, "severity": g.severity.value} for g in node_gaps]

        # Generate body
        if llm_provider and corpus_dir:
            body = _generate_body_with_llm(node, enrichment, corpus_dir, llm_provider)
        else:
            body = _generate_template_body(node, enrichment)

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
    """Get the ID registry from an enriched model (set during capsule generation).

    Returns dict mapping BPMN node ID → {capsule_id, intent_id, contract_id, slug, triple_type}.
    Returns empty dict if capsule generation hasn't run yet.
    """
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


def _generate_template_body(node, enrichment) -> str:
    """Generate a template body without LLM (--skip-llm mode)."""
    name = node.name or node.id
    body = f"# {name}\n\n"
    body += "## Purpose\n\n<!-- TODO: Describe the purpose of this task -->\n\n"
    body += "## Procedure\n\n<!-- TODO: Add step-by-step procedure -->\n\n"
    body += "## Business Rules\n\n<!-- TODO: Add business rules -->\n\n"
    body += "## Inputs Required\n\n| Input | Source | Description |\n|-------|--------|-------------|\n| <!-- TODO --> | | |\n\n"
    body += "## Outputs Produced\n\n| Output | Destination | Description |\n|--------|-------------|-------------|\n| <!-- TODO --> | | |\n\n"
    body += "## Exception Handling\n\n<!-- TODO: Add exception handling -->\n\n"
    body += "## Regulatory Context\n\n<!-- TODO: Add regulatory context -->\n\n"
    body += "## Notes\n\n<!-- Generated by mda-cli without LLM. Fill in manually or re-run with LLM. -->\n"
    return body


def _generate_body_with_llm(node, enrichment, corpus_dir, llm_provider) -> str:
    """Generate body using LLM with corpus content."""
    from llm.prompts.capsule import CAPSULE_SYSTEM, build_capsule_body_prompt

    corpus_content = []
    if enrichment and enrichment.procedure.found:
        for match in enrichment.procedure.corpus_refs[:3]:
            doc_path = _find_corpus_doc(corpus_dir, match.corpus_id)
            if doc_path:
                fm, body = frontmatter_mod.read_frontmatter_file(doc_path)
                corpus_content.append({
                    "corpus_id": match.corpus_id,
                    "title": fm.get("title", ""),
                    "doc_type": fm.get("doc_type", ""),
                    "body_text": body[:2000],
                })

    if enrichment and enrichment.regulatory.applicable:
        for match in enrichment.regulatory.corpus_refs[:2]:
            doc_path = _find_corpus_doc(corpus_dir, match.corpus_id)
            if doc_path:
                fm, body = frontmatter_mod.read_frontmatter_file(doc_path)
                corpus_content.append({
                    "corpus_id": match.corpus_id,
                    "title": fm.get("title", ""),
                    "doc_type": fm.get("doc_type", ""),
                    "body_text": body[:1500],
                })

    node_context = {
        "name": node.name or node.id,
        "element_type": node.element_type,
        "lane_name": node.lane_name,
        "predecessor_names": [],
        "successor_names": [],
    }

    prompt = build_capsule_body_prompt(node_context, corpus_content, {})
    response = llm_provider.complete(prompt, system_prompt=CAPSULE_SYSTEM, max_tokens=4096)
    return response.content


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
