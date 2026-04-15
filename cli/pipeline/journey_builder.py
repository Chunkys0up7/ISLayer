"""Journey Builder — Constructs a ProcessJourney from triple files, graph data, and job aids.

Reads all triple directories, computes topological order, data lineage,
critical path, and branch points to produce a complete process journey map.
"""

import sys
import os
from pathlib import Path
from collections import deque
from typing import Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import importlib.util


def _load_io(name):
    spec = importlib.util.spec_from_file_location(
        name,
        os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "mda_io",
            f"{name}.py",
        ),
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


frontmatter_mod = _load_io("frontmatter")
yaml_io = _load_io("yaml_io")

from models.journey import (
    ProcessJourney,
    StepSummary,
    InputSummary,
    OutputSummary,
    DataLineage,
    BranchPoint,
)


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------


def build_journey(project_root: Path, config) -> Optional[ProcessJourney]:
    """Build a ProcessJourney from all triple files on disk.

    Steps:
        1. Discover triple dirs (triples/ + decisions/)
        2. Read capsule, intent, contract frontmatter for each
        3. Find job aid files for each
        4. Read process-graph.yaml for data_objects
        5. Topological sort using predecessor/successor chains
        6. Build StepSummary for each in sorted order
        7. Build DataLineage from graph data_objects + intent inputs/outputs
        8. Detect branch points (gateways with >1 successor)
        9. Compute critical path (longest path through DAG)
       10. Compute health summary
    """
    triples_path = config.get("paths.triples") or config.get("output.triples_dir") or "triples"
    decisions_path = config.get("paths.decisions") or config.get("output.decisions_dir") or "decisions"
    triples_dir = project_root / triples_path
    decisions_dir = project_root / decisions_path

    process_id = config.get("process.id", "unknown")
    process_name = config.get("process.name", project_root.name.replace("-", " ").title())

    # 1. Discover triple directories
    triple_dirs = _discover_triple_dirs(triples_dir, decisions_dir)
    if not triple_dirs:
        return None

    # 2-3. Read capsule data for each triple dir
    capsule_data = {}  # capsule_id -> dict with all frontmatter + derived data
    capsule_names = {}  # capsule_id -> human name

    for td, section in triple_dirs:
        data = _read_triple_dir(td, section)
        if data and data.get("capsule_id"):
            cid = data["capsule_id"]
            capsule_data[cid] = data
            capsule_names[cid] = data.get("name", td.name)

    if not capsule_data:
        return None

    # 4. Read process-graph.yaml for data_objects
    graph_data = _read_graph_data(project_root, config)

    # 5. Topological sort
    sorted_ids = topological_sort(capsule_data)

    # 6. Build StepSummary for each
    steps = []
    for step_num, cid in enumerate(sorted_ids, start=1):
        cd = capsule_data[cid]
        step = _build_step_summary(step_num, cid, cd, capsule_names)
        steps.append(step)

    # 7. Build DataLineage
    data_lineage = build_data_lineage(graph_data, capsule_data, capsule_names)

    # 8. Detect branch points
    branch_points = detect_branch_points(steps, capsule_data)

    # 9. Compute critical path
    critical_path = compute_critical_path(steps, capsule_data)

    # 10. Health summary
    health_summary = _compute_health_summary(steps)

    journey = ProcessJourney(
        process_name=process_name,
        process_id=process_id,
        total_steps=len(steps),
        steps=steps,
        data_lineage=data_lineage,
        critical_path=critical_path,
        branch_points=branch_points,
        health_summary=health_summary,
    )
    return journey


# ---------------------------------------------------------------------------
# Discovery
# ---------------------------------------------------------------------------


def _discover_triple_dirs(triples_dir: Path, decisions_dir: Path) -> list[tuple[Path, str]]:
    """Find all triple directories. Returns (path, section) tuples."""
    dirs = []
    for base, section in [(triples_dir, "tasks"), (decisions_dir, "decisions")]:
        if not base or not base.exists():
            continue
        for d in sorted(base.iterdir()):
            if d.is_dir() and not d.name.startswith("_"):
                # Must contain at least a capsule file
                if list(d.glob("*.cap.md")):
                    dirs.append((d, section))
    return dirs


# ---------------------------------------------------------------------------
# Reading triple data
# ---------------------------------------------------------------------------


def _read_triple_dir(triple_dir: Path, section: str) -> dict:
    """Read capsule, intent, contract frontmatter and job aid from a triple dir."""
    data = {"section": section, "slug": triple_dir.name, "dir": triple_dir}

    # Capsule
    cap_files = list(triple_dir.glob("*.cap.md"))
    if not cap_files:
        return data
    cap_fm, _ = frontmatter_mod.read_frontmatter_file(cap_files[0])
    data["capsule_id"] = cap_fm.get("capsule_id", "")
    data["name"] = cap_fm.get("bpmn_task_name", triple_dir.name)
    data["task_type"] = cap_fm.get("bpmn_task_type", "unknown")
    data["owner"] = cap_fm.get("owner_role")
    data["status"] = cap_fm.get("status", "draft")
    data["predecessor_ids"] = cap_fm.get("predecessor_ids", []) or []
    data["successor_ids"] = cap_fm.get("successor_ids", []) or []
    data["bpmn_task_id"] = cap_fm.get("bpmn_task_id", "")
    data["binding_status"] = cap_fm.get("binding_status", cap_fm.get("status", "unknown"))

    # Intent
    int_files = list(triple_dir.glob("*.int.md"))
    if int_files:
        int_fm, _ = frontmatter_mod.read_frontmatter_file(int_files[0])
        data["intent_fm"] = int_fm
        data["intent_inputs"] = int_fm.get("required_inputs", []) or []
        data["intent_outputs"] = int_fm.get("outputs", []) or []
        data["preconditions"] = int_fm.get("preconditions", []) or []
        data["invariants"] = int_fm.get("invariants", []) or []
        data["events_emitted"] = int_fm.get("events_emitted", int_fm.get("domain_events", [])) or []
        data["sources"] = int_fm.get("source_systems", []) or []
        data["sinks"] = int_fm.get("target_systems", int_fm.get("sink_systems", [])) or []
    else:
        data["intent_fm"] = {}
        data["intent_inputs"] = []
        data["intent_outputs"] = []
        data["preconditions"] = []
        data["invariants"] = []
        data["events_emitted"] = []
        data["sources"] = []
        data["sinks"] = []

    # Contract
    ict_files = list(triple_dir.glob("*.ict.md"))
    if ict_files:
        ict_fm, _ = frontmatter_mod.read_frontmatter_file(ict_files[0])
        data["contract_fm"] = ict_fm
    else:
        data["contract_fm"] = {}

    # Job Aid
    ja_files = list(triple_dir.glob("*.jobaid.yaml"))
    if ja_files:
        try:
            ja_data = yaml_io.read_yaml(ja_files[0])
            data["jobaid_id"] = ja_data.get("jobaid_id", ja_files[0].stem)
            data["jobaid_dimensions"] = list(ja_data.get("dimensions", {}).keys()) if isinstance(ja_data.get("dimensions"), dict) else []
            rules = ja_data.get("rules", [])
            data["jobaid_rule_count"] = len(rules) if isinstance(rules, list) else 0
        except Exception:
            data["jobaid_id"] = None
            data["jobaid_dimensions"] = []
            data["jobaid_rule_count"] = 0
    else:
        data["jobaid_id"] = None
        data["jobaid_dimensions"] = []
        data["jobaid_rule_count"] = 0

    # Health score from existing report data (if available)
    data["health_score"] = 0.0
    data["gaps"] = []

    return data


def _read_graph_data(project_root: Path, config) -> dict:
    """Read process-graph.yaml if it exists."""
    graph_path = project_root / "process-graph.yaml"
    if not graph_path.exists():
        # Try output dir
        output_dir = project_root / (config.get("paths.output") or config.get("output.output_dir") or "output")
        graph_path = output_dir / "process-graph.yaml"

    if graph_path.exists():
        try:
            return yaml_io.read_yaml(graph_path)
        except Exception:
            return {}
    return {}


# ---------------------------------------------------------------------------
# Topological Sort (Kahn's Algorithm)
# ---------------------------------------------------------------------------


def topological_sort(capsule_data: dict) -> list[str]:
    """Topologically sort capsule IDs using Kahn's algorithm on predecessor/successor DAG.

    Handles cycles by appending remaining nodes at the end.
    """
    # Build adjacency list and in-degree count
    all_ids = set(capsule_data.keys())
    adj = {cid: [] for cid in all_ids}  # cid -> list of successors
    in_degree = {cid: 0 for cid in all_ids}

    for cid, cd in capsule_data.items():
        for succ in cd.get("successor_ids", []):
            if succ in all_ids:
                adj[cid].append(succ)
                in_degree[succ] = in_degree.get(succ, 0) + 1

    # Start with nodes that have no predecessors
    queue = deque()
    for cid in all_ids:
        if in_degree[cid] == 0:
            queue.append(cid)

    # Stable sort: process in alphabetical order when multiple nodes have 0 in-degree
    queue = deque(sorted(queue))
    result = []

    while queue:
        node = queue.popleft()
        result.append(node)
        for succ in sorted(adj.get(node, [])):
            in_degree[succ] -= 1
            if in_degree[succ] == 0:
                queue.append(succ)

    # Handle cycles: append remaining nodes
    remaining = [cid for cid in sorted(all_ids) if cid not in result]
    if remaining:
        import warnings
        warnings.warn(
            f"Cycle detected in process graph. {len(remaining)} nodes appended at end: "
            + ", ".join(remaining[:5])
        )
        result.extend(remaining)

    return result


# ---------------------------------------------------------------------------
# Critical Path (longest path via DP)
# ---------------------------------------------------------------------------


def compute_critical_path(steps: list[StepSummary], capsule_data: dict) -> list[str]:
    """Compute the critical path (longest path through the DAG) via DP.

    For each node in topological order:
        longest_to[node] = max(longest_to[pred] + 1 for pred in predecessors)
    Then backtrack from the node with the highest value.
    """
    all_ids = {s.capsule_id for s in steps}
    if not all_ids:
        return []

    # Build predecessor map
    pred_map = {}  # cid -> list of predecessor cids
    succ_map = {}  # cid -> list of successor cids
    for cid, cd in capsule_data.items():
        if cid not in all_ids:
            continue
        preds = [p for p in cd.get("predecessor_ids", []) if p in all_ids]
        pred_map[cid] = preds
        succs = [s for s in cd.get("successor_ids", []) if s in all_ids]
        succ_map[cid] = succs

    # Use existing step order (already topologically sorted)
    topo_order = [s.capsule_id for s in steps]

    longest_to = {cid: 1 for cid in topo_order}
    prev_on_path = {cid: None for cid in topo_order}

    for cid in topo_order:
        for pred in pred_map.get(cid, []):
            if pred in longest_to:
                candidate = longest_to[pred] + 1
                if candidate > longest_to[cid]:
                    longest_to[cid] = candidate
                    prev_on_path[cid] = pred

    if not longest_to:
        return []

    # Find the end of the critical path
    end_node = max(longest_to, key=longest_to.get)

    # Backtrack
    path = []
    current = end_node
    while current is not None:
        path.append(current)
        current = prev_on_path.get(current)
    path.reverse()

    return path


# ---------------------------------------------------------------------------
# Data Lineage
# ---------------------------------------------------------------------------


def build_data_lineage(
    graph_data: dict, capsule_data: dict, capsule_names: dict
) -> list[DataLineage]:
    """Build data lineage from process-graph.yaml data_objects and intent inputs/outputs.

    Graph data_objects format:
        data_objects:
          - id: borrower_profile
            produced_by: Task_ReceiveRequest  # BPMN task ID or "external"
            consumed_by: [Task_ClassifyEmployment, Task_VerifyW2]

    Maps BPMN task IDs to capsule IDs using capsule frontmatter bpmn_task_id.
    Falls back to inferring lineage from intent inputs/outputs.
    """
    lineage_items = []

    # Build bpmn_task_id -> capsule_id mapping
    bpmn_to_capsule = {}
    for cid, cd in capsule_data.items():
        btid = cd.get("bpmn_task_id", "")
        if btid:
            bpmn_to_capsule[btid] = cid

    # From process-graph.yaml data_objects
    data_objects = graph_data.get("data_objects", [])
    seen_data = set()

    if isinstance(data_objects, list):
        for dobj in data_objects:
            if not isinstance(dobj, dict):
                continue
            data_id = dobj.get("id", "")
            if not data_id:
                continue

            produced_by = dobj.get("produced_by", "external")
            if produced_by == "external":
                source = "external"
                source_name = "External System"
            else:
                source = bpmn_to_capsule.get(produced_by, produced_by)
                source_name = capsule_names.get(source, produced_by)

            consumers = []
            for consumer_id in dobj.get("consumed_by", []):
                ccid = bpmn_to_capsule.get(consumer_id, consumer_id)
                consumers.append({
                    "capsule_id": ccid,
                    "name": capsule_names.get(ccid, consumer_id),
                })

            lineage_items.append(DataLineage(
                data_name=data_id,
                source=source,
                source_name=source_name,
                consumers=consumers,
            ))
            seen_data.add(data_id.lower().replace("-", "_").replace(" ", "_"))

    # Fallback: infer from intent inputs/outputs
    if not lineage_items:
        # Collect all outputs by name
        output_producers = {}  # output_name -> (capsule_id, name)
        for cid, cd in capsule_data.items():
            for out in cd.get("intent_outputs", []):
                out_name = out.get("name", "") if isinstance(out, dict) else str(out)
                if out_name:
                    output_producers[out_name.lower().replace("-", "_").replace(" ", "_")] = (cid, capsule_names.get(cid, cid))

        # Match inputs to outputs
        input_consumers = {}  # normalized_name -> list of (capsule_id, name)
        for cid, cd in capsule_data.items():
            for inp in cd.get("intent_inputs", []):
                inp_name = inp.get("name", "") if isinstance(inp, dict) else str(inp)
                if inp_name:
                    key = inp_name.lower().replace("-", "_").replace(" ", "_")
                    if key not in input_consumers:
                        input_consumers[key] = []
                    input_consumers[key].append({
                        "capsule_id": cid,
                        "name": capsule_names.get(cid, cid),
                    })

        # Build lineage from matched names
        all_data_names = set(output_producers.keys()) | set(input_consumers.keys())
        for dname in sorted(all_data_names):
            norm = dname.lower().replace("-", "_").replace(" ", "_")
            if norm in seen_data:
                continue

            if dname in output_producers:
                source, source_name = output_producers[dname]
            else:
                source = "external"
                source_name = "External System"

            consumers = input_consumers.get(dname, [])

            lineage_items.append(DataLineage(
                data_name=dname.replace("_", " ").title(),
                source=source,
                source_name=source_name,
                consumers=consumers,
            ))

    return lineage_items


# ---------------------------------------------------------------------------
# Branch Points
# ---------------------------------------------------------------------------


def detect_branch_points(
    steps: list[StepSummary], capsule_data: dict
) -> list[BranchPoint]:
    """Detect branch points — steps (typically gateways) with multiple successors."""
    branch_points = []
    step_names = {s.capsule_id: s.name for s in steps}

    for step in steps:
        cd = capsule_data.get(step.capsule_id, {})
        successors = cd.get("successor_ids", [])
        if len(successors) > 1:
            branches = []
            for succ_id in successors:
                branches.append({
                    "condition": "",  # Would need edge data for conditions
                    "target_capsule_id": succ_id,
                    "target_name": step_names.get(succ_id, succ_id),
                })
            branch_points.append(BranchPoint(
                gateway_capsule_id=step.capsule_id,
                gateway_name=step.name,
                branches=branches,
            ))

    return branch_points


# ---------------------------------------------------------------------------
# StepSummary builder
# ---------------------------------------------------------------------------


def _build_step_summary(
    step_number: int, capsule_id: str, cd: dict, capsule_names: dict
) -> StepSummary:
    """Build a StepSummary from capsule data dict."""
    # Parse inputs
    required_inputs = []
    for inp in cd.get("intent_inputs", []):
        if isinstance(inp, dict):
            required_inputs.append(InputSummary(
                name=inp.get("name", ""),
                source=inp.get("source", "unknown"),
                schema_ref=inp.get("schema_ref") or inp.get("schema"),
                required=inp.get("required", True),
            ))
        elif isinstance(inp, str):
            required_inputs.append(InputSummary(name=inp, source="unknown"))

    # Parse outputs
    outputs = []
    for out in cd.get("intent_outputs", []):
        if isinstance(out, dict):
            outputs.append(OutputSummary(
                name=out.get("name", ""),
                type=out.get("type", "unknown"),
                sink=out.get("sink", ""),
                invariants=out.get("invariants", []) or [],
            ))
        elif isinstance(out, str):
            outputs.append(OutputSummary(name=out, type="unknown", sink=""))

    # Predecessor/successor human-readable names
    pred_names = [capsule_names.get(p, p) for p in cd.get("predecessor_ids", [])]
    succ_names = [capsule_names.get(s, s) for s in cd.get("successor_ids", [])]

    return StepSummary(
        step_number=step_number,
        capsule_id=capsule_id,
        name=cd.get("name", capsule_id),
        task_type=cd.get("task_type", "unknown"),
        owner=cd.get("owner"),
        preconditions=cd.get("preconditions", []),
        required_inputs=required_inputs,
        predecessor_steps=pred_names,
        outputs=outputs,
        invariants=cd.get("invariants", []),
        events_emitted=cd.get("events_emitted", []),
        successor_steps=succ_names,
        sources=cd.get("sources", []),
        sinks=cd.get("sinks", []),
        jobaid_id=cd.get("jobaid_id"),
        jobaid_dimensions=cd.get("jobaid_dimensions", []),
        jobaid_rule_count=cd.get("jobaid_rule_count", 0),
        health_score=cd.get("health_score", 0.0),
        gaps=cd.get("gaps", []),
        binding_status=cd.get("binding_status", "unknown"),
        slug=cd.get("slug", ""),
        section=cd.get("section", "tasks"),
    )


# ---------------------------------------------------------------------------
# Health summary
# ---------------------------------------------------------------------------


def _compute_health_summary(steps: list[StepSummary]) -> dict:
    """Compute aggregate health metrics from steps."""
    if not steps:
        return {"total_steps": 0, "avg_health": 0.0, "steps_with_gaps": 0, "total_gaps": 0}

    total_gaps = sum(len(s.gaps) for s in steps)
    steps_with_gaps = sum(1 for s in steps if s.gaps)
    scores = [s.health_score for s in steps if s.health_score > 0]
    avg_health = sum(scores) / len(scores) if scores else 0.0

    bound = sum(1 for s in steps if s.binding_status in ("approved", "bound", "active"))
    draft = sum(1 for s in steps if s.binding_status == "draft")
    review = sum(1 for s in steps if s.binding_status in ("review", "in_review"))

    with_jobaid = sum(1 for s in steps if s.jobaid_id)

    return {
        "total_steps": len(steps),
        "avg_health": round(avg_health, 1),
        "steps_with_gaps": steps_with_gaps,
        "total_gaps": total_gaps,
        "binding_counts": {"bound": bound, "draft": draft, "review": review},
        "steps_with_jobaid": with_jobaid,
        "total_inputs": sum(len(s.required_inputs) for s in steps),
        "total_outputs": sum(len(s.outputs) for s in steps),
        "total_events": sum(len(s.events_emitted) for s in steps),
    }
