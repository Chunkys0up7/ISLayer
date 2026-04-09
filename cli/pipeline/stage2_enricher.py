"""Stage 2: Corpus Enricher — Match corpus documents to BPMN nodes."""
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

def run_enricher(
    parsed_model: ParsedModel,
    corpus_dir: Path,
    llm_provider=None,  # Optional LLMProvider for disambiguation
) -> EnrichedModel:
    """Execute Stage 2: Enrich parsed model with corpus matches."""
    from datetime import datetime

    # Load corpus index
    index_path = corpus_dir / "corpus.config.yaml"
    if not index_path.exists():
        # No corpus — everything becomes gaps
        return _create_empty_enrichment(parsed_model)

    index_data = yaml_io.read_yaml(index_path)
    corpus_index = CorpusIndex.from_dict(index_data)

    enriched = EnrichedModel(
        parsed_model=parsed_model,
        enrichment_date=datetime.utcnow().isoformat(),
        enriched_by="mda-cli",
    )

    process_domain = ""
    if parsed_model.processes:
        process_domain = parsed_model.processes[0].name or ""

    for node in parsed_model.nodes:
        node_enrichment = _enrich_node(node, corpus_index, corpus_dir, process_domain, parsed_model, llm_provider)
        enriched.node_enrichments[node.id] = node_enrichment

        # Generate gaps for missing enrichments
        gaps = _generate_gaps(node, node_enrichment)
        enriched.gaps.extend(gaps)

    return enriched

def _enrich_node(node, corpus_index, corpus_dir, process_domain, parsed_model, llm_provider) -> NodeEnrichment:
    """Enrich a single node."""
    ne = NodeEnrichment(node_id=node.id)

    # Procedure lookup
    procedure_matches = _score_corpus_matches(
        node, corpus_index, process_domain, parsed_model,
        doc_type_filter="procedure"
    )
    if procedure_matches:
        ne.procedure = ProcedureEnrichment(found=True, corpus_refs=procedure_matches)

    # Ownership resolution
    if node.lane_name:
        ne.ownership = OwnershipEnrichment(resolved=True, owner_role=node.lane_name, source="lane")

    # Decision rules (for gateways and businessRuleTasks)
    if node.element_type in ("exclusiveGateway", "inclusiveGateway", "eventBasedGateway", "businessRuleTask"):
        # Check for condition expressions on outgoing edges
        outgoing_edges = [e for e in parsed_model.edges if e.source_id == node.id]
        has_conditions = any(e.condition_expression for e in outgoing_edges)

        rule_matches = _score_corpus_matches(node, corpus_index, process_domain, parsed_model, doc_type_filter="rule")

        if has_conditions or rule_matches:
            conditions = [{"flow_id": e.id, "expression": e.condition_expression} for e in outgoing_edges if e.condition_expression]
            ne.decision_rules = DecisionRuleEnrichment(
                defined=True,
                rule_type="condition_expression" if has_conditions else "kb_document",
                rule_ref=rule_matches[0].corpus_id if rule_matches else None,
                conditions=conditions,
            )
        else:
            ne.decision_rules = DecisionRuleEnrichment(defined=False)

    # Regulatory context
    reg_matches = _score_corpus_matches(node, corpus_index, process_domain, parsed_model, doc_type_filter="regulation")
    pol_matches = _score_corpus_matches(node, corpus_index, process_domain, parsed_model, doc_type_filter="policy")
    if reg_matches or pol_matches:
        ne.regulatory = RegulatoryEnrichment(
            applicable=True,
            corpus_refs=reg_matches + pol_matches,
        )

    # Integration binding
    sys_matches = _score_corpus_matches(node, corpus_index, process_domain, parsed_model, doc_type_filter="system")
    if sys_matches:
        ne.integration = IntegrationEnrichment(has_binding=True, system_name=sys_matches[0].corpus_id)

    return ne


def _score_corpus_matches(node, corpus_index, process_domain, parsed_model, doc_type_filter=None) -> list[CorpusMatch]:
    """Multi-factor scoring algorithm matching corpus entries to a node."""
    results = []

    process_ids = [p.id for p in parsed_model.processes]

    for entry in corpus_index.documents:
        if doc_type_filter and entry.doc_type != doc_type_filter:
            continue

        score = 0.0
        match_method = "none"

        applies = entry.applies_to

        # Factor 1: Process ID match + task name pattern match (score 1.0)
        process_match = bool(set(getattr(applies, 'process_ids', []) if isinstance(applies, AppliesTo) else applies.get('process_ids', [])).intersection(process_ids))
        patterns = getattr(applies, 'task_name_patterns', []) if isinstance(applies, AppliesTo) else applies.get('task_name_patterns', [])
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

        # Factor 2: Domain + task type match (score 0.5)
        task_types = getattr(applies, 'task_types', []) if isinstance(applies, AppliesTo) else applies.get('task_types', [])
        domain_match = process_domain.lower() in entry.domain.lower() if process_domain else False
        type_match = node.element_type in task_types
        if domain_match and type_match and score < 0.5:
            score = 0.5
            match_method = "domain_type"

        # Factor 3: Tag intersection (score 0.3)
        if node.name and score < 0.3:
            name_tokens = set(node.name.lower().replace("-", " ").replace("_", " ").split())
            stop_words = {"the", "a", "an", "and", "or", "to", "for", "of", "in", "on", "is", "at"}
            name_tokens -= stop_words
            doc_tags = set(t.lower() for t in entry.tags)
            overlap = name_tokens.intersection(doc_tags)
            if overlap:
                score = max(score, 0.3)
                match_method = "tag_intersection"

        # Factor 4: Role match (bonus +0.1)
        roles = getattr(applies, 'roles', []) if isinstance(applies, AppliesTo) else applies.get('roles', [])
        if node.lane_name and roles:
            if node.lane_name in roles:
                score += 0.1

        if score >= 0.3:
            confidence = "high" if score >= 0.8 else "medium" if score >= 0.5 else "low"
            results.append(CorpusMatch(
                corpus_id=entry.corpus_id,
                match_confidence=confidence,
                match_method=match_method,
                match_score=score,
            ))

    results.sort(key=lambda x: x.match_score, reverse=True)
    return results


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
