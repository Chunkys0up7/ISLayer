"""mda parse <bpmn-file> -- Parse BPMN XML into typed object model."""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def run_parse(args, config):
    """Parse a BPMN file and output the typed model."""
    import json
    from pipeline.stage1_parser import run_parser, get_parse_summary
    from mda_io.yaml_io import write_yaml, dump_yaml_string
    from output.console import print_header, print_success, print_table, print_info
    from output.json_output import output_json

    model = run_parser(args.bpmn_file, config.ontology_dir)
    summary = get_parse_summary(model)

    if args.json:
        output_json(model.to_dict())
        return

    # Display summary
    print_header(f"Parsed: {args.bpmn_file.name}")

    # Print node type counts
    type_rows = [[ntype, str(count)] for ntype, count in summary["node_types"].items()]
    if type_rows:
        print_table("Node Types", ["Type", "Count"], type_rows)

    # Print overall stats
    print_info(f"  Processes: {summary['processes']}")
    print_info(f"  Total nodes: {summary['total_nodes']}")
    print_info(f"  Edges: {summary['edges']}")
    print_info(f"  Lanes: {summary['lanes']}")
    print_info(f"  Data objects: {summary['data_objects']}")
    print_info(f"  Message flows: {summary['message_flows']}")

    # Write output if requested
    if args.output:
        if args.format == "json":
            with open(args.output, "w", encoding="utf-8") as f:
                json.dump(model.to_dict(), f, indent=2)
        else:
            write_yaml(args.output, model.to_dict())
        print_success(f"Written to {args.output}")
    elif not args.json:
        # Print to stdout
        print(dump_yaml_string(model.to_dict()))
