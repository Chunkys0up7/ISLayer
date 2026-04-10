"""Pipeline orchestrator — chain stages for ingest and reingest."""
from pathlib import Path
from typing import Optional

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .stage1_parser import run_parser, get_parse_summary
from .stage2_enricher import run_enricher
from .stage3_capsule_gen import run_capsule_generator
from .stage4_intent_gen import run_intent_generator
from .stage5_contract_gen import run_contract_generator
from .stage6_validator import run_validator
from .graph_builder import build_graph_from_registry

def run_ingest(
    bpmn_path: Path,
    config,  # Config object
    llm_provider=None,
    skip_llm: bool = False,
    stages: Optional[list[int]] = None,
    no_validate: bool = False,
) -> dict:
    """Full pipeline: BPMN to triples.

    Returns a summary dict with counts and results.
    """
    stages = stages or [1, 2, 3, 4, 5, 6]
    results = {"stages": {}, "files_created": [], "gaps": 0}

    provider = None if skip_llm else llm_provider

    model = None
    enriched = None

    # Stage 1: Parse
    if 1 in stages:
        model = run_parser(bpmn_path, config.ontology_dir)
        results["stages"][1] = get_parse_summary(model)

    # Stage 2: Enrich
    if 2 in stages:
        if model is None:
            raise ValueError("Stage 2 requires Stage 1 (parsed model). Include stage 1 or provide a pre-parsed model.")
        enriched = run_enricher(model, config.corpus_dir, llm_provider=provider)
        results["stages"][2] = enriched.gap_summary()
        results["gaps"] = len(enriched.gaps)

    # Stage 3: Generate capsules
    triples_dir = config.resolve_path("paths.triples")
    triples_dir.mkdir(parents=True, exist_ok=True)

    config_dict = config.to_dict()

    if 3 in stages:
        if enriched is None:
            raise ValueError("Stage 3 requires Stage 2 (enriched model). Include stages 1-2.")
        capsule_files = run_capsule_generator(
            enriched, triples_dir, config_dict,
            corpus_dir=config.corpus_dir if not skip_llm else None,
            llm_provider=provider,
        )
        results["stages"][3] = {"capsules_created": len(capsule_files)}
        results["files_created"].extend(capsule_files)

    # Stage 4: Generate intents
    if 4 in stages:
        if enriched is None:
            raise ValueError("Stage 4 requires Stage 2 (enriched model). Include stages 1-2.")
        intent_files = run_intent_generator(
            enriched, triples_dir, config_dict,
            llm_provider=provider,
        )
        results["stages"][4] = {"intents_created": len(intent_files)}
        results["files_created"].extend(intent_files)

    # Stage 5: Generate contracts
    if 5 in stages:
        if enriched is None:
            raise ValueError("Stage 5 requires Stage 2 (enriched model). Include stages 1-2.")
        contract_files = run_contract_generator(
            enriched, triples_dir, config_dict,
            llm_provider=provider,
        )
        results["stages"][5] = {"contracts_created": len(contract_files)}
        results["files_created"].extend(contract_files)

    # Build process graph (after capsule generation sets up the ID registry)
    if 3 in stages and enriched is not None:
        graph_dir_path = config.get("paths.graph") or config.get("output.graph_dir") or "graph"
        graph_dir = config.project_root / graph_dir_path
        graph = build_graph_from_registry(enriched, graph_dir, config_dict)
        results["graph"] = {
            "nodes": graph.get("node_count", 0),
            "edges": graph.get("edge_count", 0),
            "connected": graph.get("connected", False),
        }

    # Stage 6: Validate
    if 6 in stages and not no_validate:
        decisions_dir = config.resolve_path("paths.decisions")
        schemas_dir = config.schemas_dir
        report = run_validator(triples_dir, decisions_dir, schemas_dir)
        results["stages"][6] = report.to_dict()

    return results
