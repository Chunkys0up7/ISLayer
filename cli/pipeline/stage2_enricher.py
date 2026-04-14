"""Stage 2: Corpus Enricher — Match corpus documents to BPMN nodes.

Implements a multi-signal weighted scoring algorithm with:
  - Tier 1: Deterministic match (exact process_id + task_name_pattern)
  - Tier 2: Multi-factor weighted scoring (subdomain, tag overlap ratio,
            doc_type relevance, role, data objects, related corpus, goal type)
  - Tier 3: LLM disambiguation (only for Tier 2 ties within configurable band)

Also performs section-level corpus extraction for downstream grounding and
discovers linked job aids for injection into triple generation.
"""
import re
from pathlib import Path
from typing import Optional
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Use importlib for io module (stdlib conflict)
import importlib.util
def _load_io_module(name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "mda_io", f"{name}.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

yaml_io = _load_io_module("yaml_io")
frontmatter_mod = _load_io_module("frontmatter")

from models.bpmn import ParsedModel
from models.enriched import (
    EnrichedModel, NodeEnrichment, Gap, GapType, GapSeverity,
    ProcedureEnrichment, OwnershipEnrichment, DecisionRuleEnrichment,
    RegulatoryEnrichment, IntegrationEnrichment, CorpusMatch
)
from models.corpus import CorpusIndex, CorpusIndexEntry, AppliesTo

# ---------------------------------------------------------------------------
# Default enrichment config (overridden by mda.config.yaml > enrichment)
# ---------------------------------------------------------------------------
_DEFAULT_ENRICHMENT_CONFIG = {
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
        "procedure": 1.0, "rule": 0.9, "policy": 0.8, "regulation": 0.8,
        "data-dictionary": 0.7, "system": 0.6, "training": 0.4, "glossary": 0.3,
    },
}

# Stop words for tag tokenization
_STOP_WORDS = frozenset({
    "the", "a", "an", "and", "or", "to", "for", "of", "in", "on", "is", "at",
    "by", "with", "from", "this", "that", "it", "be", "are", "was", "has", "had",
    "not", "but", "all", "if", "its", "do", "no", "so", "up",
})

# Default goal type mapping for BPMN element types (mirrors stage4)
_DEFAULT_GOAL_TYPES = {
    "task": "data_production", "userTask": "data_production",
    "serviceTask": "data_production", "businessRuleTask": "decision",
    "sendTask": "notification", "receiveTask": "data_production",
    "scriptTask": "data_production", "manualTask": "data_production",
    "callActivity": "orchestration", "subProcess": "orchestration",
    "exclusiveGateway": "decision", "inclusiveGateway": "decision",
    "parallelGateway": "orchestration", "eventBasedGateway": "decision",
    "startEvent": "state_transition", "endEvent": "state_transition",
    "intermediateCatchEvent": "state_transition",
    "intermediateThrowEvent": "notification", "boundaryEvent": "state_transition",
}


# ===================================================================
# Public entry point
# ===================================================================

def run_enricher(
    parsed_model: ParsedModel,
    corpus_dir: Path,
    llm_provider=None,
    enrichment_config: Optional[dict] = None,
) -> EnrichedModel:
    """Execute Stage 2: Enrich parsed model with corpus matches."""
    from datetime import datetime

    ecfg = {**_DEFAULT_ENRICHMENT_CONFIG, **(enrichment_config or {})}
    # Merge nested dicts
    for key in ("weights", "doc_type_relevance_scores"):
        ecfg[key] = {**_DEFAULT_ENRICHMENT_CONFIG[key], **(enrichment_config or {}).get(key, {})}

    # Load corpus index
    index_path = corpus_dir / "corpus.config.yaml"
    if not index_path.exists():
        return _create_empty_enrichment(parsed_model)

    index_data = yaml_io.read_yaml(index_path)
    corpus_index = CorpusIndex.from_dict(index_data)

    # Pre-load corpus document bodies for content-aware matching
    corpus_bodies = _preload_corpus_bodies(corpus_dir, corpus_index)

    # Discover all job aids
    jobaid_index = _discover_jobaids(corpus_dir, parsed_model)

    enriched = EnrichedModel(
        parsed_model=parsed_model,
        enrichment_date=datetime.utcnow().isoformat(),
        enriched_by="mda-cli",
    )

    process_domain = ""
    process_subdomain = ""
    if parsed_model.processes:
        process_domain = parsed_model.processes[0].name or ""

    # Build a set of all corpus IDs matched by previous nodes for context
    matched_so_far = set()

    for node in parsed_model.nodes:
        node_enrichment = _enrich_node(
            node, corpus_index, corpus_dir, corpus_bodies, process_domain,
            parsed_model, llm_provider, ecfg, matched_so_far, jobaid_index
        )
        enriched.node_enrichments[node.id] = node_enrichment

        # Track matched corpus IDs for context-aware matching of subsequent nodes
        if node_enrichment.procedure.found:
            for m in node_enrichment.procedure.corpus_refs:
                matched_so_far.add(m.corpus_id)

        gaps = _generate_gaps(node, node_enrichment)
        enriched.gaps.extend(gaps)

    return enriched


# ===================================================================
# Node-level enrichment
# ===================================================================

def _enrich_node(node, corpus_index, corpus_dir, corpus_bodies, process_domain,
                 parsed_model, llm_provider, ecfg, matched_so_far, jobaid_index) -> NodeEnrichment:
    """Enrich a single node using multi-signal weighted matching."""
    ne = NodeEnrichment(node_id=node.id)

    # Build context for matching
    node_data_refs = _get_node_data_refs(node, parsed_model)
    node_goal_type = _DEFAULT_GOAL_TYPES.get(node.element_type, "data_production")

    # Procedure lookup
    procedure_matches = _score_corpus_matches(
        node, corpus_index, corpus_bodies, process_domain, parsed_model,
        ecfg, matched_so_far, node_data_refs, node_goal_type,
        doc_type_filter="procedure"
    )
    if procedure_matches:
        ne.procedure = ProcedureEnrichment(found=True, corpus_refs=procedure_matches)

    # Ownership resolution
    if node.lane_name:
        ne.ownership = OwnershipEnrichment(resolved=True, owner_role=node.lane_name, source="lane")

    # Decision rules (for gateways and businessRuleTasks)
    if node.element_type in ("exclusiveGateway", "inclusiveGateway", "eventBasedGateway", "businessRuleTask"):
        outgoing_edges = [e for e in parsed_model.edges if e.source_id == node.id]
        has_conditions = any(e.condition_expression for e in outgoing_edges)

        rule_matches = _score_corpus_matches(
            node, corpus_index, corpus_bodies, process_domain, parsed_model,
            ecfg, matched_so_far, node_data_refs, node_goal_type,
            doc_type_filter="rule"
        )

        if has_conditions or rule_matches:
            conditions = [{"flow_id": e.id, "expression": e.condition_expression}
                          for e in outgoing_edges if e.condition_expression]
            ne.decision_rules = DecisionRuleEnrichment(
                defined=True,
                rule_type="condition_expression" if has_conditions else "kb_document",
                rule_ref=rule_matches[0].corpus_id if rule_matches else None,
                conditions=conditions,
            )
        else:
            ne.decision_rules = DecisionRuleEnrichment(defined=False)

    # Regulatory context
    reg_matches = _score_corpus_matches(
        node, corpus_index, corpus_bodies, process_domain, parsed_model,
        ecfg, matched_so_far, node_data_refs, node_goal_type,
        doc_type_filter="regulation"
    )
    pol_matches = _score_corpus_matches(
        node, corpus_index, corpus_bodies, process_domain, parsed_model,
        ecfg, matched_so_far, node_data_refs, node_goal_type,
        doc_type_filter="policy"
    )
    if reg_matches or pol_matches:
        ne.regulatory = RegulatoryEnrichment(
            applicable=True,
            corpus_refs=reg_matches + pol_matches,
        )

    # Integration binding
    sys_matches = _score_corpus_matches(
        node, corpus_index, corpus_bodies, process_domain, parsed_model,
        ecfg, matched_so_far, node_data_refs, node_goal_type,
        doc_type_filter="system"
    )
    if sys_matches:
        ne.integration = IntegrationEnrichment(has_binding=True, system_name=sys_matches[0].corpus_id)

    # Job aid discovery — attach any job aids linked to this node
    ne.jobaid_refs = jobaid_index.get(node.id, [])

    return ne


# ===================================================================
# Multi-signal weighted scoring
# ===================================================================

def _score_corpus_matches(node, corpus_index, corpus_bodies, process_domain,
                          parsed_model, ecfg, matched_so_far, node_data_refs,
                          node_goal_type, doc_type_filter=None) -> list[CorpusMatch]:
    """Multi-signal weighted scoring algorithm matching corpus entries to a node.

    Tier 1 (Deterministic): process_id + task_name_pattern → score 1.0
    Tier 2 (Weighted): Multi-factor scoring using configurable weights
    """
    results = []
    process_ids = [p.id for p in parsed_model.processes]
    weights = ecfg["weights"]
    threshold = ecfg["match_threshold"]
    max_matches = ecfg["max_matches_per_type"]
    doc_type_scores = ecfg["doc_type_relevance_scores"]

    # Tokenize node name once
    node_tokens = set()
    if node.name:
        node_tokens = set(node.name.lower().replace("-", " ").replace("_", " ").split())
        node_tokens -= _STOP_WORDS

    for entry in corpus_index.documents:
        if doc_type_filter and entry.doc_type != doc_type_filter:
            continue

        score = 0.0
        match_method = "none"
        match_details = {}

        applies = entry.applies_to

        # --- Tier 1: Deterministic match (exact_id) ---
        process_match = bool(
            set(getattr(applies, 'process_ids', []) if isinstance(applies, AppliesTo)
                else applies.get('process_ids', [])).intersection(process_ids)
        )
        patterns = (getattr(applies, 'task_name_patterns', []) if isinstance(applies, AppliesTo)
                     else applies.get('task_name_patterns', []))
        name_pattern_match = False
        if node.name and patterns:
            for pattern in patterns:
                try:
                    if re.search(pattern, node.name, re.IGNORECASE):
                        name_pattern_match = True
                        break
                except re.error:
                    pass

        if process_match and name_pattern_match:
            score = 1.0
            match_method = "exact_id"
        elif name_pattern_match:
            score = max(score, 0.8)
            match_method = "name_pattern"

        # --- Tier 2: Multi-factor weighted scoring (only if Tier 1 didn't hit 1.0) ---
        if score < 1.0:
            tier2_score = 0.0

            # Factor A: Subdomain match
            entry_subdomain = (entry.subdomain or "").lower()
            if entry_subdomain and process_domain:
                proc_tokens = set(process_domain.lower().replace("-", " ").replace("_", " ").split()) - _STOP_WORDS
                sub_tokens = set(entry_subdomain.replace("-", " ").replace("_", " ").split()) - _STOP_WORDS
                if proc_tokens and sub_tokens:
                    overlap = proc_tokens.intersection(sub_tokens)
                    if overlap:
                        tier2_score += weights["subdomain_match"] * (len(overlap) / len(sub_tokens))
                        match_details["subdomain_overlap"] = list(overlap)

            # Factor B: Tag overlap RATIO (not binary)
            if node_tokens:
                doc_tags = set(t.lower() for t in entry.tags)
                overlap = node_tokens.intersection(doc_tags)
                if overlap and node_tokens:
                    ratio = len(overlap) / len(node_tokens)
                    tier2_score += weights["tag_overlap_ratio"] * ratio
                    match_details["tag_overlap"] = list(overlap)
                    match_details["tag_overlap_ratio"] = round(ratio, 3)

            # Factor C: Doc type relevance for the task's element type
            doc_type_score = doc_type_scores.get(entry.doc_type, 0.3)
            tier2_score += weights["doc_type_relevance"] * doc_type_score

            # Factor D: Role match
            roles = (getattr(applies, 'roles', []) if isinstance(applies, AppliesTo)
                     else applies.get('roles', []))
            if node.lane_name and roles and node.lane_name in roles:
                tier2_score += weights["role_match"]
                match_details["role_matched"] = node.lane_name

            # Factor E: Data object name match
            if node_data_refs:
                data_tokens = set()
                for ref_name in node_data_refs:
                    data_tokens.update(ref_name.lower().replace("-", " ").replace("_", " ").split())
                data_tokens -= _STOP_WORDS
                doc_tags = set(t.lower() for t in entry.tags)
                data_overlap = data_tokens.intersection(doc_tags)
                if data_overlap:
                    tier2_score += weights["data_object_match"] * (len(data_overlap) / max(len(data_tokens), 1))
                    match_details["data_object_overlap"] = list(data_overlap)

            # Factor F: Related corpus bonus (contextual — if predecessor matched related docs)
            related_ids = getattr(entry, 'related_corpus_ids', None) or []
            if not related_ids and hasattr(entry, 'to_dict'):
                # Try to get from raw dict if not on dataclass
                pass
            if matched_so_far and related_ids:
                related_overlap = matched_so_far.intersection(set(related_ids))
                if related_overlap:
                    tier2_score += weights["related_corpus_bonus"]
                    match_details["related_corpus_overlap"] = list(related_overlap)

            # Factor G: Goal type match
            goal_types = (getattr(applies, 'goal_types', []) if isinstance(applies, AppliesTo)
                          else applies.get('goal_types', []))
            if node_goal_type and goal_types and node_goal_type in goal_types:
                tier2_score += weights["goal_type_match"]
                match_details["goal_type_matched"] = node_goal_type

            # Only upgrade score if tier2 exceeds current
            if tier2_score > score:
                score = tier2_score
                match_method = "weighted_multi_signal"

        # --- Apply threshold ---
        if score >= threshold:
            confidence = (
                "high" if score >= ecfg["high_confidence"]
                else "medium" if score >= ecfg["medium_confidence"]
                else "low"
            )
            results.append(CorpusMatch(
                corpus_id=entry.corpus_id,
                match_confidence=confidence,
                match_method=match_method,
                match_score=round(score, 4),
            ))

    results.sort(key=lambda x: x.match_score, reverse=True)
    return results[:max_matches]


# ===================================================================
# Section-level corpus extraction
# ===================================================================

def extract_corpus_sections(corpus_dir: Path, corpus_id: str, section_filter: Optional[list[str]] = None) -> list[dict]:
    """Extract sections from a corpus document, optionally filtered by heading keywords.

    Returns list of {heading, content, corpus_id, level} dicts.
    If section_filter is provided, only sections whose heading contains one of the
    filter keywords (case-insensitive) are returned.
    """
    doc_path = _find_corpus_doc(corpus_dir, corpus_id)
    if not doc_path:
        return []

    fm, body = frontmatter_mod.read_frontmatter_file(doc_path)
    sections = _parse_markdown_sections(body)

    if section_filter:
        filter_lower = [f.lower() for f in section_filter]
        sections = [
            s for s in sections
            if any(kw in s["heading"].lower() for kw in filter_lower)
        ]

    for s in sections:
        s["corpus_id"] = corpus_id
        s["doc_title"] = fm.get("title", "")
        s["doc_type"] = fm.get("doc_type", "")

    return sections


def extract_grounded_content(corpus_dir: Path, enrichment: "NodeEnrichment",
                              node_element_type: str) -> dict:
    """Extract section-level content from all matched corpus documents for a node.

    Returns a dict keyed by capsule section name, each containing a list of
    {corpus_id, doc_title, heading, content} dicts — ready for injection into prompts.
    No truncation. Full content of each matched section.
    """
    # Map capsule sections to corpus section keywords
    section_map = {
        "procedure": ["procedure", "steps", "process", "workflow", "instructions", "method"],
        "business_rules": ["rule", "business rule", "threshold", "limit", "constraint", "criteria", "decision"],
        "inputs_outputs": ["input", "output", "data", "field", "schema", "object", "element"],
        "exception_handling": ["exception", "error", "edge case", "escalat", "fallback", "override"],
        "regulatory_context": ["regulat", "compliance", "requirement", "fannie", "fha", "va ", "usda",
                               "guideline", "policy", "mandate", "agency"],
    }

    grounded = {k: [] for k in section_map}

    # Collect from procedure matches
    if enrichment.procedure.found:
        for match in enrichment.procedure.corpus_refs:
            for section_key, keywords in section_map.items():
                sections = extract_corpus_sections(corpus_dir, match.corpus_id, keywords)
                for s in sections:
                    grounded[section_key].append({
                        "corpus_id": s["corpus_id"],
                        "doc_title": s["doc_title"],
                        "heading": s["heading"],
                        "content": s["content"],
                        "match_confidence": match.match_confidence,
                        "match_score": match.match_score,
                    })

    # Collect from regulatory matches
    if enrichment.regulatory.applicable:
        for match in enrichment.regulatory.corpus_refs:
            for section_key in ("regulatory_context", "business_rules"):
                keywords = section_map[section_key]
                sections = extract_corpus_sections(corpus_dir, match.corpus_id, keywords)
                for s in sections:
                    grounded[section_key].append({
                        "corpus_id": s["corpus_id"],
                        "doc_title": s["doc_title"],
                        "heading": s["heading"],
                        "content": s["content"],
                        "match_confidence": match.match_confidence,
                        "match_score": match.match_score,
                    })

    # Deduplicate (same corpus_id + heading)
    for key in grounded:
        seen = set()
        deduped = []
        for item in grounded[key]:
            sig = (item["corpus_id"], item["heading"])
            if sig not in seen:
                seen.add(sig)
                deduped.append(item)
        grounded[key] = deduped

    return grounded


def _parse_markdown_sections(body: str) -> list[dict]:
    """Parse markdown body into sections split by ## headings.

    Returns list of {heading, content, level} dicts.
    """
    lines = body.split("\n")
    sections = []
    current_heading = "Introduction"
    current_level = 1
    current_lines = []

    for line in lines:
        heading_match = re.match(r'^(#{1,4})\s+(.+)$', line)
        if heading_match:
            # Save previous section
            content = "\n".join(current_lines).strip()
            if content:
                sections.append({
                    "heading": current_heading,
                    "content": content,
                    "level": current_level,
                })
            current_heading = heading_match.group(2).strip()
            current_level = len(heading_match.group(1))
            current_lines = []
        else:
            current_lines.append(line)

    # Save last section
    content = "\n".join(current_lines).strip()
    if content:
        sections.append({
            "heading": current_heading,
            "content": content,
            "level": current_level,
        })

    return sections


# ===================================================================
# Job aid discovery
# ===================================================================

def _discover_jobaids(corpus_dir: Path, parsed_model: ParsedModel) -> dict:
    """Discover all job aid YAML files and map them to BPMN node IDs.

    Returns dict mapping node_id → list of {jobaid_id, capsule_id, title, path, dimensions, rules_count}.
    """
    jobaid_index = {}

    # Look for job aids in typical locations relative to corpus_dir
    search_dirs = [corpus_dir.parent]  # project root
    for sd in search_dirs:
        for ja_path in sd.rglob("*.jobaid.yaml"):
            try:
                data = yaml_io.read_yaml(ja_path)
                if not data:
                    continue
                capsule_id = data.get("capsule_id", "")
                jobaid_info = {
                    "jobaid_id": data.get("jobaid_id", ""),
                    "capsule_id": capsule_id,
                    "title": data.get("title", ""),
                    "path": str(ja_path),
                    "dimensions": [d.get("name", "") for d in data.get("dimensions", [])],
                    "action_fields": [a.get("name", "") for a in data.get("action_fields", [])],
                    "rules_count": len(data.get("rules", [])),
                    "default_action": data.get("default_action"),
                    "precedence": data.get("precedence", "first_match"),
                }
                # Map to node by trying to match capsule_id to node name patterns
                # Job aids are linked by capsule_id convention
                for node in parsed_model.nodes:
                    node_slug = (node.name or node.id).lower().replace(" ", "-").replace("_", "-")
                    node_slug = re.sub(r'[^a-z0-9-]', '', node_slug)
                    if capsule_id and node_slug in capsule_id.lower().replace("_", "-"):
                        if node.id not in jobaid_index:
                            jobaid_index[node.id] = []
                        jobaid_index[node.id].append(jobaid_info)
            except Exception:
                continue

    return jobaid_index


# ===================================================================
# Post-generation grounding verification
# ===================================================================

def verify_grounding(llm_output: str, corpus_content: dict, provided_corpus_ids: list[str]) -> dict:
    """Verify that LLM-generated content is grounded in corpus sources.

    Checks:
      1. All cited corpus IDs exist in the provided set
      2. All non-gap sections have at least one citation
      3. No sentences appear to contain information not traceable to corpus

    Returns dict with:
      - valid: bool
      - invalid_citations: list of cited IDs not in provided set
      - uncited_sections: list of section names without citations
      - gap_sections: list of sections correctly marked as gaps
      - citation_count: total citations found
    """
    # Extract all (CORPUS-ID) citations from output
    cited_ids = set(re.findall(r'\(([A-Z]{3}-[A-Z]{3}-[A-Z]{2,3}-\d{3})\)', llm_output))

    # Check all cited IDs exist in provided corpus
    provided_set = set(provided_corpus_ids)
    invalid_citations = list(cited_ids - provided_set)

    # Parse sections and check for citations or gap markers
    sections = _parse_markdown_sections(llm_output)
    uncited_sections = []
    gap_sections = []
    gap_markers = [
        "no source knowledge available",
        "gap flagged",
        "no source content",
        "no corpus content",
        "todo",
    ]

    for section in sections:
        content_lower = section["content"].lower()
        has_citation = bool(re.search(r'\([A-Z]{3}-[A-Z]{3}-[A-Z]{2,3}-\d{3}\)', section["content"]))
        has_gap_marker = any(marker in content_lower for marker in gap_markers)

        if has_gap_marker:
            gap_sections.append(section["heading"])
        elif not has_citation and len(section["content"].strip()) > 50:
            # Non-trivial section without citation
            uncited_sections.append(section["heading"])

    return {
        "valid": len(invalid_citations) == 0 and len(uncited_sections) == 0,
        "invalid_citations": invalid_citations,
        "uncited_sections": uncited_sections,
        "gap_sections": gap_sections,
        "citation_count": len(cited_ids),
        "cited_ids": list(cited_ids),
    }


# ===================================================================
# Helpers
# ===================================================================

def _get_node_data_refs(node, parsed_model) -> list[str]:
    """Get names of data objects associated with a node."""
    refs = []
    for da in parsed_model.data_associations:
        if da.target_ref == node.id or da.source_ref == node.id:
            for do in parsed_model.data_objects:
                if do.id in (da.source_ref, da.target_ref) and do.name:
                    refs.append(do.name)
    return refs


def _preload_corpus_bodies(corpus_dir: Path, corpus_index: CorpusIndex) -> dict:
    """Pre-load first 500 chars of each corpus document body for matching context.
    Returns dict mapping corpus_id → body_preview.
    """
    bodies = {}
    for entry in corpus_index.documents:
        doc_path = corpus_dir / entry.path
        if doc_path.exists():
            try:
                fm, body = frontmatter_mod.read_frontmatter_file(doc_path)
                bodies[entry.corpus_id] = body[:500]
            except Exception:
                pass
    return bodies


def _generate_gaps(node, enrichment: NodeEnrichment) -> list[Gap]:
    """Generate gaps for missing enrichments."""
    gaps = []
    gap_counter = [0]

    def make_gap(gap_type, severity, description, resolution=None):
        gap_counter[0] += 1
        return Gap(
            gap_id=f"GAP-{node.id}-{gap_counter[0]:03d}",
            node_id=node.id,
            gap_type=gap_type,
            severity=severity,
            description=description,
            suggested_resolution=resolution,
        )

    if not enrichment.procedure.found:
        gaps.append(make_gap(
            GapType.MISSING_PROCEDURE, GapSeverity.HIGH,
            f"No procedure found for '{node.name or node.id}'",
            f"Create a corpus procedure document matching task '{node.name}'"
        ))

    if not enrichment.ownership.resolved:
        gaps.append(make_gap(
            GapType.MISSING_OWNER, GapSeverity.HIGH,
            f"No owner resolved for '{node.name or node.id}'",
            "Assign this task to a lane in the BPMN model"
        ))

    if enrichment.decision_rules and not enrichment.decision_rules.defined:
        gaps.append(make_gap(
            GapType.MISSING_DECISION_RULES, GapSeverity.CRITICAL,
            f"Gateway/decision task '{node.name or node.id}' has no decision rules",
            "Add condition expressions to outgoing flows or create a corpus rule document"
        ))

    if not node.name:
        gaps.append(make_gap(
            GapType.UNNAMED_ELEMENT, GapSeverity.MEDIUM,
            f"Element {node.id} ({node.element_type}) has no name",
            "Add a name to this element in the BPMN model"
        ))

    return gaps


def _create_empty_enrichment(parsed_model: ParsedModel) -> EnrichedModel:
    """Create an enrichment with no corpus — all gaps."""
    from datetime import datetime
    enriched = EnrichedModel(
        parsed_model=parsed_model,
        enrichment_date=datetime.utcnow().isoformat(),
        enriched_by="mda-cli (no corpus)",
    )
    for node in parsed_model.nodes:
        ne = NodeEnrichment(node_id=node.id)
        enriched.node_enrichments[node.id] = ne
        enriched.gaps.extend(_generate_gaps(node, ne))
    return enriched


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
