"""mda generate <type> -- Generate triple artifacts via LLM."""

import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def run_generate(args, config):
    """Generate capsule, intent, or contract files from an enriched model."""
    from models.enriched import EnrichedModel
    from mda_io.yaml_io import read_yaml
    from output.console import print_header, print_success, print_info, print_warning
    from output.json_output import output_json

    gen_type = args.type  # capsule, intent, contract, all

    # Load enriched model
    enriched_path = getattr(args, "enriched_model", None)
    if not enriched_path:
        # Try default location
        enriched_path = config.resolve_path("paths.triples").parent / "enriched-model.yaml"

    if not enriched_path.exists():
        raise FileNotFoundError(
            f"Enriched model not found at {enriched_path}. "
            f"Run 'mda enrich' first or specify --enriched-model."
        )

    if str(enriched_path).endswith(".json"):
        with open(enriched_path) as f:
            enriched_data = json.load(f)
    else:
        enriched_data = read_yaml(enriched_path)

    enriched = EnrichedModel.from_dict(enriched_data)

    # Get LLM provider
    llm_provider = None
    if not getattr(args, "skip_llm", False):
        try:
            from llm.provider import get_provider
            llm_provider = get_provider(config)
        except Exception as e:
            print_warning(f"LLM provider unavailable ({e}), generating template stubs")

    config_dict = config.to_dict()
    triples_dir = config.resolve_path("paths.triples")
    triples_dir.mkdir(parents=True, exist_ok=True)

    # Filter nodes if --nodes specified
    node_filter = None
    if hasattr(args, "nodes") and args.nodes:
        node_filter = set(args.nodes.split(","))

    results = {"files_created": []}

    # Generate capsules
    if gen_type in ("capsule", "all"):
        from pipeline.stage3_capsule_gen import run_capsule_generator
        capsule_files = run_capsule_generator(
            enriched, triples_dir, config_dict,
            corpus_dir=config.corpus_dir if llm_provider else None,
            llm_provider=llm_provider,
        )
        results["capsules_created"] = len(capsule_files)
        results["files_created"].extend(capsule_files)

    # Generate intents
    if gen_type in ("intent", "all"):
        from pipeline.stage4_intent_gen import run_intent_generator
        intent_files = run_intent_generator(
            enriched, triples_dir, config_dict,
            llm_provider=llm_provider,
        )
        results["intents_created"] = len(intent_files)
        results["files_created"].extend(intent_files)

    # Generate contracts
    if gen_type in ("contract", "all"):
        from pipeline.stage5_contract_gen import run_contract_generator
        contract_files = run_contract_generator(
            enriched, triples_dir, config_dict,
            llm_provider=llm_provider,
        )
        results["contracts_created"] = len(contract_files)
        results["files_created"].extend(contract_files)

    if getattr(args, "json", False):
        output_json({
            k: (len(v) if isinstance(v, list) else v)
            for k, v in results.items()
        })
        return

    # Display results
    print_header(f"Generate: {gen_type}")
    for key, val in results.items():
        if key == "files_created":
            continue
        print_info(f"  {key}: {val}")

    for f in results["files_created"]:
        print_success(f"  Created {f}")
