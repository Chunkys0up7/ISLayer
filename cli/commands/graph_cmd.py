"""mda graph -- Generate process graph visualization."""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def run_graph(args, config):
    """Build a process graph from capsule frontmatter and output in various formats."""
    from mda_io.frontmatter import read_frontmatter_file
    from mda_io.yaml_io import write_yaml, dump_yaml_string
    from output.console import print_header, print_success
    from output.json_output import output_json

    triples_dir = config.resolve_path("paths.triples")
    decisions_dir = config.resolve_path("paths.decisions")

    # Build graph from capsule frontmatter
    nodes = []
    edges = []

    for base_dir in [triples_dir, decisions_dir]:
        if not base_dir.exists():
            continue
        for d in sorted(base_dir.iterdir()):
            if not d.is_dir() or d.name.startswith("_"):
                continue
            for cap in d.glob("*.cap.md"):
                fm, _ = read_frontmatter_file(cap)
                node = {
                    "id": fm.get("capsule_id", d.name),
                    "name": fm.get("bpmn_task_name", d.name),
                    "type": fm.get("bpmn_task_type", "unknown"),
                    "status": fm.get("status", "draft"),
                    "lane": fm.get("owner_role"),
                }
                nodes.append(node)

                # Build edges from successor IDs
                for succ in fm.get("successor_ids", []):
                    edges.append({
                        "from": fm.get("capsule_id", d.name),
                        "to": succ,
                    })

    graph = {
        "process": config.get("process.name", "Unknown"),
        "node_count": len(nodes),
        "edge_count": len(edges),
        "nodes": nodes,
        "edges": edges,
    }

    if args.format == "mermaid":
        mermaid = _to_mermaid(graph)
        if args.output:
            args.output.write_text(mermaid, encoding="utf-8")
            print_success(f"Written to {args.output}")
        else:
            print(mermaid)
    elif args.format == "dot":
        dot = _to_dot(graph)
        if args.output:
            args.output.write_text(dot, encoding="utf-8")
            print_success(f"Written to {args.output}")
        else:
            print(dot)
    else:
        # YAML format (default)
        if getattr(args, "json", False):
            output_json(graph)
        elif args.output:
            write_yaml(args.output, graph)
            print_success(f"Written to {args.output}")
        else:
            print_header(f"Process Graph: {graph['process']}")
            print(dump_yaml_string(graph))


def _to_mermaid(graph: dict) -> str:
    """Convert graph dict to Mermaid flowchart syntax."""
    lines = ["graph TD"]
    for node in graph["nodes"]:
        nid = node["id"].replace("-", "_")
        label = node["name"] or node["id"]
        node_type = node.get("type", "")
        if node_type in (
            "exclusiveGateway",
            "inclusiveGateway",
            "eventBasedGateway",
        ):
            lines.append(f"    {nid}{{{{{label}}}}}")
        elif node_type in ("startEvent", "endEvent"):
            lines.append(f"    {nid}(({label}))")
        else:
            lines.append(f'    {nid}["{label}"]')
    for edge in graph["edges"]:
        src = edge["from"].replace("-", "_")
        tgt = edge["to"].replace("-", "_")
        lines.append(f"    {src} --> {tgt}")
    return "\n".join(lines)


def _to_dot(graph: dict) -> str:
    """Convert graph dict to Graphviz DOT syntax."""
    lines = ["digraph process {", "    rankdir=TD;", '    node [shape=box];']
    for node in graph["nodes"]:
        nid = node["id"].replace("-", "_")
        label = node["name"] or node["id"]
        node_type = node.get("type", "")
        if "Gateway" in node_type:
            shape = "diamond"
        elif node_type in ("startEvent", "endEvent"):
            shape = "circle"
        else:
            shape = "box"
        lines.append(f'    {nid} [label="{label}", shape={shape}];')
    for edge in graph["edges"]:
        src = edge["from"].replace("-", "_")
        tgt = edge["to"].replace("-", "_")
        lines.append(f"    {src} -> {tgt};")
    lines.append("}")
    return "\n".join(lines)
