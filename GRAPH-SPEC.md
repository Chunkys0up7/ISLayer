# MDA Intent Layer -- Graph Builder & ID Registry Specification

> Recreation specification for the two-pass capsule generation approach and
> process graph builder introduced to fix cross-reference connectivity bugs.

| Field            | Value                                      |
|------------------|--------------------------------------------|
| Modules          | `cli/pipeline/stage3_capsule_gen.py`, `cli/pipeline/graph_builder.py`, `cli/pipeline/orchestrator.py` |
| Status           | Implemented                                |
| Tests            | 537 passing                                |

---

## 1. Problem Statement

The original Stage 3 capsule generator used a single-pass approach that
assigned IDs and generated files in one traversal. Predecessor and successor
references were constructed with hardcoded `-001` suffixes:

```
predecessor_ids: ["CAP-XX-VER-001"]
```

When multiple BPMN nodes mapped to the same three-letter category code (e.g.,
two tasks both containing "verify" would both map to `VER`), every
predecessor/successor reference pointed to the first node in that category
(`-001`) regardless of which node was actually connected in the BPMN graph.
This produced wrong cross-references in capsule frontmatter and a disconnected
process graph.

---

## 2. Solution: Two-Pass Capsule Generation

Stage 3 (`cli/pipeline/stage3_capsule_gen.py`) now uses two explicit passes
over the enriched model's node list.

### 2.1 Pass 1 -- Build ID Registry

Iterate all nodes in `enriched.parsed_model.nodes`. For each node whose
element mapping has `generates_capsule: true` (the default):

1. Derive a three-letter category code from the node name via
   `_derive_category()`.
2. Maintain a `seq_counter` dict keyed by `"{id_prefix}-{category}"`. Increment
   the counter for this key to get the next sequence number.
3. Assign three IDs using the sequence number zero-padded to three digits:

   | ID Type     | Pattern                            | Example              |
   |-------------|------------------------------------|----------------------|
   | capsule_id  | `CAP-{prefix}-{category}-{seq}`    | `CAP-XX-VER-002`     |
   | intent_id   | `INT-{prefix}-{category}-{seq}`    | `INT-XX-VER-002`     |
   | contract_id | `ICT-{prefix}-{category}-{seq}`    | `ICT-XX-VER-002`     |

4. Compute a URL-safe slug from the node name (lowercase, hyphens, strip
   non-alphanumeric).
5. Look up `triple_type`, `generates_intent`, and `generates_contract` from
   the ontology element mapping.
6. Store the result in `id_registry[node.id]`:

```python
id_registry[node.id] = {
    "capsule_id": capsule_id,
    "intent_id": intent_id,
    "contract_id": contract_id,
    "slug": slug,
    "triple_type": triple_type,        # "standard" | "decision"
    "generates_intent": bool,
    "generates_contract": bool,
}
```

After the loop, attach the registry to the enriched model:

```python
enriched.id_registry = id_registry
```

This makes it available to Stages 4, 5, and the graph builder without passing
it as a separate argument.

### 2.2 Pass 2 -- Generate Files

Iterate `enriched.parsed_model.nodes` a second time. For each node present in
`id_registry`:

1. **Predecessor IDs** -- call `enriched.parsed_model.get_predecessors(node.id)`,
   look up each predecessor's BPMN ID in `id_registry`, collect the actual
   `capsule_id` values.
2. **Successor IDs** -- same approach via `get_successors(node.id)`.
3. **Exception IDs** -- iterate `node.boundary_event_ids`, look up each in
   `id_registry`.
4. Build frontmatter dict with correct `predecessor_ids`, `successor_ids`,
   `exception_ids` lists containing real capsule IDs.
5. Generate body (template or LLM-assisted).
6. Route to output subdirectory: `decisions/{slug}/` for `triple_type ==
   "decision"`, otherwise `triples/{slug}/`.
7. Write `{slug}.cap.md` via `frontmatter_mod.write_frontmatter_file()`.

### 2.3 ID Registry API

```python
def get_id_registry(enriched: EnrichedModel) -> dict:
    """Return the ID registry attached during capsule generation.

    Returns dict mapping BPMN node ID -> {capsule_id, intent_id,
    contract_id, slug, triple_type, generates_intent, generates_contract}.
    Returns empty dict if capsule generation has not run.
    """
    return getattr(enriched, 'id_registry', {})
```

Consumers call this to read the registry without depending on the attribute
name.

---

## 3. Graph Builder (`cli/pipeline/graph_builder.py`)

### 3.1 Two Modes

The graph builder provides two entry points for different use cases:

| Function                     | When Used                                  |
|------------------------------|--------------------------------------------|
| `build_graph_from_registry`  | During `mda ingest`, after Stage 3 has run and `enriched.id_registry` is populated. Uses in-memory data for speed and accuracy. |
| `build_graph_from_disk`      | During `mda graph` standalone command. Reads `.cap.md` files from `triples/` and `decisions/` directories, extracts frontmatter, and reconstructs the graph. |

#### `build_graph_from_registry(enriched, output_dir, config) -> dict`

1. Read `id_registry` from `enriched.id_registry`.
2. For each BPMN node in the registry, create a node dict.
3. For each node, iterate its successors via
   `enriched.parsed_model.get_successors()`. For each successor present in the
   registry, create an edge. Look up condition expressions from
   `enriched.parsed_model.edges`.
4. Compute metrics (see 3.3).
5. Write `process-graph.yaml` and `graph-visual.md`.
6. Return the graph dict.

#### `build_graph_from_disk(triples_dir, decisions_dir, output_dir, config) -> dict`

1. Scan `triples_dir` and `decisions_dir` for subdirectories containing
   `.cap.md` files. Skip directories starting with `_`.
2. Read frontmatter from each capsule file.
3. Build nodes from frontmatter fields (`capsule_id`, `intent_id`,
   `contract_id`, `bpmn_task_id`, `bpmn_task_name`, `bpmn_task_type`,
   `owner_role`, `status`).
4. Build edges from `successor_ids` in frontmatter, deduplicating via a
   `seen_edges` set.
5. Infer start/end nodes: start nodes have no incoming edges; end nodes have
   no outgoing edges.
6. Compute metrics and write output files.
7. Return the graph dict.

### 3.2 Output Files

Both modes write two files to `output_dir`:

| File                  | Format   | Contents                                    |
|-----------------------|----------|---------------------------------------------|
| `process-graph.yaml`  | YAML     | Structured graph: metadata, nodes, edges, metrics |
| `graph-visual.md`     | Markdown | Mermaid flowchart with styled node classes  |

### 3.3 Graph Metrics

Computed for every graph and included in `process-graph.yaml`:

| Metric        | Type    | Description                                          |
|---------------|---------|------------------------------------------------------|
| `node_count`  | int     | Total number of nodes in the graph                   |
| `edge_count`  | int     | Total number of directed edges                       |
| `start_events`| int     | Count of start event nodes                           |
| `end_events`  | int     | Count of end event nodes                             |
| `connected`   | bool    | Whether all nodes are reachable from the start node  |

**Connectivity check** uses undirected BFS from the first start node (or first
node if no start events). The adjacency list treats edges as bidirectional for
reachability. `connected` is `true` when the set of visited nodes equals the
set of all nodes in the graph.

Registry mode uses `visited == all_cap_ids` (exact equality). Disk mode uses
`visited >= all_cap_ids` (superset, tolerating nodes referenced in edges but
missing from disk).

### 3.4 Mermaid Generation

`_generate_mermaid(graph)` produces a Mermaid `graph TD` flowchart.

**Node shapes by element type:**

| Element Type                                        | Mermaid Shape         | Syntax                 |
|-----------------------------------------------------|-----------------------|------------------------|
| Task types (userTask, serviceTask, scriptTask, etc.) | Rectangle             | `[" "]`                |
| exclusiveGateway, inclusiveGateway, eventBasedGateway| Diamond               | `{{ }}`                |
| startEvent                                          | Double circle          | `((" "))`              |
| endEvent                                            | Double circle          | `((" "))`              |
| boundaryEvent                                       | Trapezoid             | `[/" "\]`              |

**Edge labels:** If an edge has a `condition` expression, it is truncated to
30 characters and rendered as `-->|"condition"| target`.

**Style classes:**

| Class    | Fill      | Stroke    | Applied To      |
|----------|-----------|-----------|-----------------|
| task     | `#e1f5fe` | `#01579b` | All task types   |
| gateway  | `#fff3e0` | `#e65100` | All gateways     |
| event    | `#e8f5e9` | `#1b5e20` | All events       |

Node IDs in Mermaid have hyphens replaced with underscores to comply with
Mermaid identifier rules.

### 3.5 Process Graph YAML Format

```yaml
process_id: "ML-001"
process_name: "Mortgage Loan Origination"
node_count: 24
edge_count: 27
start_events: 1
end_events: 2
connected: true
nodes:
  - capsule_id: "CAP-ML-RCV-001"
    intent_id: "INT-ML-RCV-001"
    contract_id: "ICT-ML-RCV-001"
    bpmn_id: "Task_ReceiveApp"
    name: "Receive Application"
    type: "userTask"
    lane: "Loan Officer"
    triple_type: "standard"
edges:
  - from: "CAP-ML-RCV-001"
    to: "CAP-ML-VER-001"
    condition: null
  - from: "CAP-ML-DEC-001"
    to: "CAP-ML-REJ-001"
    condition: "score < 620"
```

---

## 4. Pipeline Integration

In `cli/pipeline/orchestrator.py`, the graph builder is invoked automatically
after Stage 3 completes:

```python
from .graph_builder import build_graph_from_registry

# Inside run_ingest(), after capsule generation:
if 3 in stages and enriched is not None:
    graph_dir_path = config.get("paths.graph") or config.get("output.graph_dir") or "graph"
    graph_dir = config.project_root / graph_dir_path
    graph = build_graph_from_registry(enriched, graph_dir, config_dict)
    results["graph"] = {
        "nodes": graph.get("node_count", 0),
        "edges": graph.get("edge_count", 0),
        "connected": graph.get("connected", False),
    }
```

The graph output directory is resolved from config keys `paths.graph` or
`output.graph_dir`, falling back to `"graph"` relative to the project root.

Graph results are included in the pipeline return dict under `results["graph"]`
with `nodes`, `edges`, and `connected` fields for reporting.

The standalone `mda graph` CLI command calls `build_graph_from_disk()` instead,
reading from existing triple files without requiring the full pipeline.

---

## 5. Category Derivation Updates

`_derive_category(name)` maps a node name to a three-letter code by scanning
for keywords (case-insensitive). The following mappings were added to support
BPMN models with event nodes and domain-specific task names:

| Keyword       | Code | Reason                                      |
|---------------|------|---------------------------------------------|
| `"start"`     | STA  | Start events                                |
| `"end"`       | END  | End events                                  |
| `"w-2"`       | W2V  | W-2 wage verification tasks                 |
| `"self-employ"`| SEI | Self-employment income tasks                |
| `"variance"`  | VAR  | Income variance analysis tasks              |

Full keyword-to-code mapping (27 entries):

```
application->APP  receive->RCV   verify->VER     credit->CRC
identity->IDV     income->INC    dti->DTI        debt->DTI
document->DOC     package->PKG   submit->SUB     underwriting->UND
appraisal->APR    order->ORD     review->MRV     validate->VAL
classify->CLS     calculate->QAL emit->NTF       notify->NTF
request->REQ      assess->ASV    eligible->DEC   threshold->DEC
complete->CMP     timeout->TMO   reject->REJ     flag->FLG
start->STA        end->END       w-2->W2V        self-employ->SEI
variance->VAR
```

**Fallback rule:** If no keyword matches, extract consonants from the name and
take the first three uppercase. If fewer than three consonants exist, take the
first three characters of the name uppercased.

---

## 6. Verification

The following conditions confirm correct operation:

1. **Correct cross-references** -- `mda ingest --skip-llm` produces capsule
   files where `predecessor_ids` and `successor_ids` contain the actual
   capsule IDs of the connected nodes (not hardcoded `-001` suffixes). Two
   nodes with the same category code receive distinct sequence numbers
   (e.g., `CAP-XX-VER-001` and `CAP-XX-VER-002`).

2. **Automatic graph generation** -- Running `mda ingest` produces
   `process-graph.yaml` and `graph-visual.md` in the configured graph
   output directory without any additional commands.

3. **Standalone graph rebuild** -- `mda graph` reads existing `.cap.md`
   files from the triples and decisions directories, reconstructs the
   graph, and writes the same two output files.

4. **Full connectivity** -- `process-graph.yaml` has `connected: true` for
   all demo processes, confirming that BFS from the start node reaches
   every node in the graph.

5. **Test suite** -- All 537 tests pass, covering ID assignment, registry
   population, cross-reference correctness, graph construction, Mermaid
   generation, and pipeline integration.

---

## 7. File Inventory

| File                                  | Role                              |
|---------------------------------------|-----------------------------------|
| `cli/pipeline/stage3_capsule_gen.py`  | Two-pass capsule generation       |
| `cli/pipeline/graph_builder.py`       | Graph construction (both modes)   |
| `cli/pipeline/orchestrator.py`        | Pipeline integration              |
| `ontology/bpmn-element-mapping.yaml`  | Element type metadata             |

---

## Appendix A: Data Flow

```
BPMN XML
  |
  v
Stage 1: Parse --> ParsedModel (nodes, edges)
  |
  v
Stage 2: Enrich --> EnrichedModel (ownership, corpus, gaps)
  |
  v
Stage 3 Pass 1: Build id_registry
  |    (enriched.id_registry = {...})
  |
  v
Stage 3 Pass 2: Generate .cap.md files with correct refs
  |
  v
Graph Builder: build_graph_from_registry()
  |    reads enriched.id_registry + parsed_model edges
  |
  v
process-graph.yaml + graph-visual.md
  |
  v
Stage 4: Intent generation (reads id_registry)
  |
  v
Stage 5: Contract generation (reads id_registry)
  |
  v
Stage 6: Validation
```
