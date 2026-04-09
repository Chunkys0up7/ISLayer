"""mda enrich <model> -- Enrich parsed model with corpus matches."""

import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def run_enrich(args, config):
    """Enrich a parsed BPMN model with corpus document matches."""
    from pipeline.stage2_enricher import run_enricher
    from models.bpmn import ParsedModel
    from mda_io.yaml_io import read_yaml, write_yaml, dump_yaml_string
    from output.console import print_header, print_success, print_info, print_table, print_warning
    from output.json_output import output_json

    # Load the parsed model
    model_path = args.model
    if not model_path.exists():
        raise FileNotFoundError(f"Parsed model not found: {model_path}")

    if str(model_path).endswith(".json"):
        with open(model_path) as f:
            model_data = json.load(f)
    else:
        model_data = read_yaml(model_path)

    parsed_model = ParsedModel.from_dict(model_data)

    # Get corpus directory
    corpus_dir = args.corpus_path if hasattr(args, "corpus_path") and args.corpus_path else config.corpus_dir

    # Get LLM provider for disambiguation (optional)
    llm_provider = None
    if not getattr(args, "skip_llm", False):
        try:
            from llm.provider import get_provider
            llm_provider = get_provider(config)
        except Exception:
            pass  # LLM is optional for enrichment

    # Run enrichment
    enriched = run_enricher(parsed_model, corpus_dir, llm_provider=llm_provider)

    if getattr(args, "json", False):
        output_json(enriched.to_dict())
        return

    # Display results
    print_header("Enrichment Results")

    # Node enrichment summary
    rows = []
    for node_id, ne in enriched.node_enrichments.items():
        node = parsed_model.get_node(node_id)
        name = node.name if node else node_id
        proc = "Y" if ne.procedure.found else "N"
        owner = ne.ownership.owner_role or "-"
        decision = "Y" if ne.decision_rules and ne.decision_rules.defined else ("-" if not ne.decision_rules else "N")
        reg = "Y" if ne.regulatory.applicable else "-"
        integ = "Y" if ne.integration.has_binding else "-"
        rows.append([name or node_id, proc, owner, decision, reg, integ])

    if rows:
        print_table(
            "Node Enrichments",
            ["Node", "Procedure", "Owner", "Decision", "Regulatory", "Integration"],
            rows,
        )

    # Gap summary
    gap_summary = enriched.gap_summary()
    print_info(f"\n  Total gaps: {gap_summary['total']}")
    if gap_summary["by_severity"]:
        for sev, count in sorted(gap_summary["by_severity"].items()):
            print_info(f"    {sev}: {count}")

    if gap_summary["total"] > 0:
        print_warning(f"{gap_summary['total']} gaps found -- run 'mda gaps' for details")

    # Write output if requested
    if hasattr(args, "output") and args.output:
        if str(args.output).endswith(".json"):
            with open(args.output, "w", encoding="utf-8") as f:
                json.dump(enriched.to_dict(), f, indent=2, default=str)
        else:
            write_yaml(args.output, enriched.to_dict())
        print_success(f"Written to {args.output}")
