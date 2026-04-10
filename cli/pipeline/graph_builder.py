"""Graph Builder — Constructs process-graph.yaml and graph-visual.md from generated triples.

This runs after capsule generation (Stage 3) and uses the id_registry to build
a correct, connected process graph with proper capsule ID references.

Can also be run standalone against existing triple files on disk.
"""

from pathlib import Path
from typing import Optional
from collections import deque
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import importlib.util
def _load_io(name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "mda_io", f"{name}.py"))
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod); return mod
frontmatter_mod = _load_io("frontmatter")
yaml_io = _load_io("yaml_io")

from models.enriched import EnrichedModel


def build_graph_from_registry(enriched: EnrichedModel, output_dir: Path, config: dict) -> dict:
    """Build process graph from the ID registry (after Stage 3).

    Uses the id_registry attached to the enriched model during capsule generation
    to produce a correct graph with proper capsule ID cross-references.

    Returns the graph dict and writes process-graph.yaml + graph-visual.md.
    """
    id_registry = getattr(enriched, 'id_registry', {})
    if not id_registry:
        return {"error": "No ID registry found. Run capsule generation first."}

    process_name = config.get("process", {}).get("name", "Unknown")
    process_id = config.get("process", {}).get("id", "Unknown")

    # Build nodes and edges from the registry + parsed model
    nodes = []
    edges = []
    node_lookup = {}  # capsule_id → node dict

    for bpmn_node in enriched.parsed_model.nodes:
        if bpmn_node.id not in id_registry:
            continue

        reg = id_registry[bpmn_node.id]
        node_dict = {
            "capsule_id": reg["capsule_id"],
            "intent_id": reg["intent_id"],
            "contract_id": reg["contract_id"],
            "bpmn_id": bpmn_node.id,
            "name": bpmn_node.name or bpmn_node.id,
            "type": bpmn_node.element_type,
            "lane": bpmn_node.lane_name,
            "triple_type": reg["triple_type"],
        }
        nodes.append(node_dict)
        node_lookup[reg["capsule_id"]] = node_dict

        # Build edges from successors
        for succ in enriched.parsed_model.get_successors(bpmn_node.id):
            if succ.id in id_registry:
                succ_reg = id_registry[succ.id]
                # Find the edge with condition expression
                condition = None
                for edge in enriched.parsed_model.edges:
                    if edge.source_id == bpmn_node.id and edge.target_id == succ.id:
                        condition = edge.condition_expression
                        break
                edges.append({
                    "from": reg["capsule_id"],
                    "to": succ_reg["capsule_id"],
                    "condition": condition,
                })

    # Compute graph metrics
    all_cap_ids = {n["capsule_id"] for n in nodes}
    start_nodes = [n for n in nodes if n["type"] == "startEvent"]
    end_nodes = [n for n in nodes if n["type"] == "endEvent"]

    # BFS connectivity
    adj = {n["capsule_id"]: set() for n in nodes}
    for e in edges:
        if e["from"] in adj:
            adj[e["from"]].add(e["to"])
        if e["to"] in adj:
            adj[e["to"]].add(e["from"])

    connected = True
    if start_nodes:
        visited = set()
        queue = deque([start_nodes[0]["capsule_id"]])
        while queue:
            nid = queue.popleft()
            if nid in visited:
                continue
            visited.add(nid)
            for neighbor in adj.get(nid, []):
                if neighbor not in visited:
                    queue.append(neighbor)
        connected = visited == all_cap_ids

    graph = {
        "process_id": process_id,
        "process_name": process_name,
        "node_count": len(nodes),
        "edge_count": len(edges),
        "start_events": len(start_nodes),
        "end_events": len(end_nodes),
        "connected": connected,
        "nodes": nodes,
        "edges": edges,
    }

    # Write outputs
    output_dir.mkdir(parents=True, exist_ok=True)
    yaml_io.write_yaml(output_dir / "process-graph.yaml", graph)

    mermaid = _generate_mermaid(graph)
    (output_dir / "graph-visual.md").write_text(
        f"# Process Flow: {process_name}\n\n```mermaid\n{mermaid}\n```\n",
        encoding="utf-8",
    )

    return graph


def build_graph_from_disk(triples_dir: Path, decisions_dir: Optional[Path], output_dir: Path, config: dict) -> dict:
    """Build process graph from existing triple files on disk.

    Reads capsule frontmatter to extract predecessor/successor IDs and builds
    the graph. Use this when running `mda graph` against existing triples.
    """
    process_name = config.get("process.name", "Unknown") if hasattr(config, 'get') and callable(config.get) else config.get("process", {}).get("name", "Unknown")
    process_id = config.get("process.id", "Unknown") if hasattr(config, 'get') and callable(config.get) else config.get("process", {}).get("id", "Unknown")

    nodes = []
    edges = []
    seen_edges = set()

    for base_dir in [triples_dir, decisions_dir]:
        if not base_dir or not base_dir.exists():
            continue
        for d in sorted(base_dir.iterdir()):
            if not d.is_dir() or d.name.startswith("_"):
                continue
            for cap_file in d.glob("*.cap.md"):
                fm, _ = frontmatter_mod.read_frontmatter_file(cap_file)

                capsule_id = fm.get("capsule_id", "")
                node_dict = {
                    "capsule_id": capsule_id,
                    "intent_id": fm.get("intent_id", ""),
                    "contract_id": fm.get("contract_id", ""),
                    "bpmn_id": fm.get("bpmn_task_id", ""),
                    "name": fm.get("bpmn_task_name", d.name),
                    "type": fm.get("bpmn_task_type", "unknown"),
                    "lane": fm.get("owner_role"),
                    "status": fm.get("status", "draft"),
                }
                nodes.append(node_dict)

                for succ_id in fm.get("successor_ids", []):
                    edge_key = (capsule_id, succ_id)
                    if edge_key not in seen_edges:
                        edges.append({"from": capsule_id, "to": succ_id})
                        seen_edges.add(edge_key)

    # Connectivity check
    all_cap_ids = {n["capsule_id"] for n in nodes}
    start_nodes = [n for n in nodes if not any(e["to"] == n["capsule_id"] for e in edges)]
    end_nodes = [n for n in nodes if not any(e["from"] == n["capsule_id"] for e in edges)]

    adj = {n["capsule_id"]: set() for n in nodes}
    for e in edges:
        if e["from"] in adj:
            adj[e["from"]].add(e["to"])
        if e["to"] in adj:
            adj[e["to"]].add(e["from"])

    connected = True
    if nodes:
        start = start_nodes[0]["capsule_id"] if start_nodes else nodes[0]["capsule_id"]
        visited = set()
        queue = deque([start])
        while queue:
            nid = queue.popleft()
            if nid in visited:
                continue
            visited.add(nid)
            for neighbor in adj.get(nid, []):
                if neighbor not in visited:
                    queue.append(neighbor)
        connected = visited >= all_cap_ids

    graph = {
        "process_id": process_id,
        "process_name": process_name,
        "node_count": len(nodes),
        "edge_count": len(edges),
        "start_events": len(start_nodes),
        "end_events": len(end_nodes),
        "connected": connected,
        "nodes": nodes,
        "edges": edges,
    }

    output_dir.mkdir(parents=True, exist_ok=True)
    yaml_io.write_yaml(output_dir / "process-graph.yaml", graph)

    mermaid = _generate_mermaid(graph)
    (output_dir / "graph-visual.md").write_text(
        f"# Process Flow: {process_name}\n\n```mermaid\n{mermaid}\n```\n",
        encoding="utf-8",
    )

    return graph


def _generate_mermaid(graph: dict) -> str:
    """Generate Mermaid flowchart from graph dict."""
    lines = ["graph TD"]

    # Node shapes by type
    for node in graph["nodes"]:
        nid = node["capsule_id"].replace("-", "_")
        label = node["name"]
        ntype = node.get("type", "task")

        if ntype in ("exclusiveGateway", "inclusiveGateway", "eventBasedGateway"):
            lines.append(f'    {nid}{{{{{label}}}}}')
        elif ntype in ("startEvent",):
            lines.append(f'    {nid}(("{label}"))')
        elif ntype in ("endEvent",):
            lines.append(f'    {nid}(("{label}"))')
        elif ntype == "boundaryEvent":
            lines.append(f'    {nid}[/"{label}"\\]')
        else:
            lines.append(f'    {nid}["{label}"]')

    # Edges
    for edge in graph["edges"]:
        src = edge["from"].replace("-", "_")
        tgt = edge["to"].replace("-", "_")
        condition = edge.get("condition")
        if condition:
            lines.append(f'    {src} -->|"{condition[:30]}"| {tgt}')
        else:
            lines.append(f'    {src} --> {tgt}')

    # Style classes
    lines.append("")
    lines.append("    classDef task fill:#e1f5fe,stroke:#01579b")
    lines.append("    classDef gateway fill:#fff3e0,stroke:#e65100")
    lines.append("    classDef event fill:#e8f5e9,stroke:#1b5e20")

    for node in graph["nodes"]:
        nid = node["capsule_id"].replace("-", "_")
        ntype = node.get("type", "task")
        if "Gateway" in ntype or "gateway" in ntype:
            lines.append(f"    class {nid} gateway")
        elif "Event" in ntype or "event" in ntype:
            lines.append(f"    class {nid} event")
        else:
            lines.append(f"    class {nid} task")

    return "\n".join(lines)
