# MDA Intent Layer -- Journey Traceability Specification

## 1. Overview

The journey traceability system traces the start-to-finish process flow of a BPMN-derived MDA process. It reads all triple directories (capsule/intent/contract frontmatter), computes a topological ordering, builds data lineage across steps, identifies branch points at gateway nodes, and computes the critical path (longest path through the DAG). The output is a `ProcessJourney` object that powers CLI display, structured export (JSON/YAML/Mermaid), and MkDocs documentation generation.

Key capabilities:

- **Step ordering** via Kahn's topological sort on the predecessor/successor DAG.
- **Data lineage** mapping every data object from its producer to all consumers.
- **Critical path** computation via longest-path dynamic programming.
- **Branch point detection** at gateway nodes with multiple successors.
- **Health summary** aggregating per-step health scores and gap counts.

Source files:

| File | Role |
|------|------|
| `cli/models/journey.py` | Data model (6 dataclasses) |
| `cli/pipeline/journey_builder.py` | Builder algorithm |
| `cli/commands/journey_cmd.py` | CLI command and console rendering |
| `templates/mkdocs/journey-index.md.j2` | MkDocs journey page template |
| `templates/mkdocs/data-lineage.md.j2` | MkDocs data lineage page template |
| `.claude/skills/mda-journey/SKILL.md` | Claude Code skill definition |
| `tests/unit/test_journey_builder.py` | Unit tests (9 tests, 5 classes) |

---

## 2. Data Model

All dataclasses live in `cli/models/journey.py`. Every class has a `to_dict()` method for serialization.

### 2.1 InputSummary

Represents a single input consumed by a step.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `name` | `str` | required | Input data object name |
| `source` | `str` | required | Producing system or capsule |
| `schema_ref` | `Optional[str]` | `None` | Reference to a schema definition |
| `required` | `bool` | `True` | Whether the input is mandatory |

### 2.2 OutputSummary

Represents a single output produced by a step.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `name` | `str` | required | Output data object name |
| `type` | `str` | required | Data type classification |
| `sink` | `str` | required | Destination system or store |
| `invariants` | `list[str]` | `[]` | Post-conditions that hold after output |

### 2.3 StepSummary

The central model representing one step in the journey. Contains all information from capsule, intent, contract, and job aid frontmatter.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `step_number` | `int` | required | Topologically sorted ordinal position |
| `capsule_id` | `str` | required | Unique capsule identifier (e.g. `CAP-IV-W2V-001`) |
| `name` | `str` | required | Human-readable step name |
| `task_type` | `str` | required | BPMN type: `task`, `gateway`, `event`, etc. |
| `owner` | `Optional[str]` | required | Role or team responsible |
| `preconditions` | `list[str]` | `[]` | Conditions that must hold before execution |
| `required_inputs` | `list[InputSummary]` | `[]` | Data inputs consumed by this step |
| `predecessor_steps` | `list[str]` | `[]` | Capsule IDs of predecessor steps |
| `outputs` | `list[OutputSummary]` | `[]` | Data outputs produced by this step |
| `invariants` | `list[str]` | `[]` | Post-conditions that hold after step |
| `events_emitted` | `list[str]` | `[]` | Domain events fired on completion |
| `successor_steps` | `list[str]` | `[]` | Capsule IDs of successor steps |
| `sources` | `list[str]` | `[]` | External systems read from |
| `sinks` | `list[str]` | `[]` | External systems written to |
| `jobaid_id` | `Optional[str]` | `None` | Associated job aid identifier |
| `jobaid_dimensions` | `list[str]` | `[]` | Job aid condition dimensions (e.g. loan_program, income_type) |
| `jobaid_rule_count` | `int` | `0` | Number of rules in the associated job aid |
| `health_score` | `float` | `0.0` | GAP health score (0-100) |
| `gaps` | `list[dict]` | `[]` | Gap entries with severity and description |
| `binding_status` | `str` | `"unknown"` | Triple lifecycle status: draft, review, approved, bound |
| `slug` | `str` | `""` | URL-safe directory name for docs links |
| `section` | `str` | `"tasks"` | Either `tasks` or `decisions` |

### 2.4 DataLineage

Tracks a single data object from its producer to all consumers.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `data_name` | `str` | required | Data object name |
| `source` | `str` | required | `"external"` or a capsule_id |
| `source_name` | `str` | required | Human-readable producer name |
| `consumers` | `list[dict]` | `[]` | List of `{capsule_id, name}` consumer entries |

### 2.5 BranchPoint

Represents a decision gateway where the process flow diverges.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `gateway_capsule_id` | `str` | required | Capsule ID of the gateway step |
| `gateway_name` | `str` | required | Human-readable gateway name |
| `branches` | `list[dict]` | `[]` | List of `{condition, target_capsule_id, target_name}` |

### 2.6 ProcessJourney

Top-level container for the complete journey.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `process_name` | `str` | required | Process display name |
| `process_id` | `str` | required | Process identifier from config |
| `total_steps` | `int` | required | Count of steps |
| `steps` | `list[StepSummary]` | `[]` | Ordered step summaries |
| `data_lineage` | `list[DataLineage]` | `[]` | All data lineage records |
| `critical_path` | `list[str]` | `[]` | Capsule IDs on the critical path |
| `branch_points` | `list[BranchPoint]` | `[]` | All detected branch points |
| `health_summary` | `dict` | `{}` | Aggregate health: avg_health, total_gaps, steps_with_jobaid, grade |

Helper methods:

- `get_step(capsule_id) -> Optional[StepSummary]` -- linear scan lookup by capsule ID.
- `get_data(data_name) -> Optional[DataLineage]` -- normalized fuzzy lookup (lowercased, hyphens/spaces replaced with underscores).

---

## 3. Journey Builder

Implementation: `cli/pipeline/journey_builder.py`

### 3.1 build_journey() Algorithm

`build_journey(project_root: Path, config) -> Optional[ProcessJourney]`

Ten sequential steps:

1. **Discover triple dirs** -- Scan `triples/` and `decisions/` directories (paths from config: `paths.triples`, `output.triples_dir` falling back to `"triples"` and `"decisions"`). Returns list of `(path, section)` tuples.
2. **Read capsule data** -- For each triple directory, read capsule/intent/contract frontmatter. Build `capsule_data` dict keyed by capsule_id and `capsule_names` dict mapping capsule_id to human name.
3. **Read job aid files** -- Locate `.jobaid.yaml` files for each capsule, extract dimensions and rule counts.
4. **Read process-graph.yaml** -- Load graph data including `data_objects` section for data lineage.
5. **Topological sort** -- Call `topological_sort(capsule_data)` to get execution order.
6. **Build StepSummary** -- For each capsule ID in sorted order, construct a `StepSummary` with step_number starting at 1. Populate inputs/outputs from intent frontmatter, predecessors/successors from capsule frontmatter, health/gaps from GAP analysis, job aid references.
7. **Build DataLineage** -- Call `build_data_lineage(graph_data, capsule_data, capsule_names)`.
8. **Detect branch points** -- Call `detect_branch_points(steps, capsule_data)`.
9. **Compute critical path** -- Call `compute_critical_path(steps, capsule_data)`.
10. **Compute health summary** -- Aggregate step health scores into `{avg_health, total_gaps, steps_with_jobaid, grade, steps_with_gaps}`.

Returns `None` if no triple directories or no capsule data found.

### 3.2 topological_sort()

`topological_sort(capsule_data: dict) -> list[str]`

Implements Kahn's algorithm:

1. **Build structures** -- Create adjacency list `adj` (capsule_id -> successor IDs) and `in_degree` counter for all capsule IDs. Only edges within the known capsule set are included.
2. **Initialize queue** -- Collect all nodes with in_degree == 0 (no predecessors). Sort alphabetically for deterministic output.
3. **Process queue** -- Dequeue a node, append to result, decrement in_degree for each successor. When a successor reaches in_degree 0, enqueue it. Successors are processed in sorted order.
4. **Cycle handling** -- After the queue is exhausted, any remaining nodes (not in result) form cycles. These are appended to the result in sorted order, and a `warnings.warn()` is emitted listing up to 5 cycle participants.

Returns: ordered list of capsule ID strings.

### 3.3 compute_critical_path()

`compute_critical_path(steps: list[StepSummary], capsule_data: dict) -> list[str]`

Longest-path dynamic programming on the topologically sorted step order:

1. **Build maps** -- Create `pred_map` (capsule_id -> predecessor IDs) and `succ_map` (capsule_id -> successor IDs) from `capsule_data`, filtering to only IDs present in steps.
2. **Initialize DP** -- `longest_to[cid] = 1` for all nodes. `prev_on_path[cid] = None` for backtracking.
3. **Forward pass** -- For each node in topological order (step list order), for each predecessor: if `longest_to[pred] + 1 > longest_to[cid]`, update `longest_to[cid]` and record `prev_on_path[cid] = pred`.
4. **Find end node** -- The node with the maximum `longest_to` value.
5. **Backtrack** -- Follow `prev_on_path` chain from end node back to a node with `prev_on_path = None`. Reverse the collected path.

Returns: ordered list of capsule IDs forming the longest path through the DAG.

### 3.4 build_data_lineage()

`build_data_lineage(graph_data: dict, capsule_data: dict, capsule_names: dict) -> list[DataLineage]`

Two-phase approach with primary and fallback sources:

**Phase 1 -- From process-graph.yaml data_objects (primary):**

1. Build `bpmn_to_capsule` mapping from capsule frontmatter `bpmn_task_id` field.
2. For each entry in `graph_data["data_objects"]`:
   - `produced_by`: if `"external"`, source is external; otherwise map BPMN task ID to capsule ID via `bpmn_to_capsule`.
   - `consumed_by`: map each BPMN task ID to capsule ID, build consumer list of `{capsule_id, name}`.
   - Create `DataLineage` record. Track seen data names (normalized) in `seen_data` set.

**Phase 2 -- Fallback from intent inputs/outputs (only if Phase 1 yields nothing):**

1. Collect all outputs from intent frontmatter: `output_producers[normalized_name] = (capsule_id, name)`.
2. Collect all inputs: `input_consumers[normalized_name] = [{capsule_id, name}, ...]`.
3. Union all data names from both maps.
4. For each name: if it appears in `output_producers`, that capsule is the source; otherwise source is `"external"`. Consumers come from `input_consumers`.
5. Data name display is title-cased with underscores converted to spaces.

Normalization: lowercase, replace hyphens and spaces with underscores.

### 3.5 detect_branch_points()

`detect_branch_points(steps: list[StepSummary], capsule_data: dict) -> list[BranchPoint]`

1. Build `step_names` lookup from step list.
2. For each step, check `capsule_data[capsule_id]["successor_ids"]`.
3. If a step has more than one successor, create a `BranchPoint` with one branch entry per successor: `{condition: "", target_capsule_id, target_name}`.
4. Condition is left empty (would require edge-level data from the BPMN model).

---

## 4. CLI Command

Implementation: `cli/commands/journey_cmd.py`

### 4.1 Command Signature

```
mda journey [--step <capsule-id>] [--data <data-name>] [--critical-path] [--format yaml|json|mermaid]
```

### 4.2 Options

| Option | Type | Description |
|--------|------|-------------|
| `--step <id>` | string | Show detailed view of a single step. Supports fuzzy matching by name substring or capsule ID substring. |
| `--data <name>` | string | Trace a single data object through its lineage (source and all consumers). |
| `--critical-path` | flag | Display only the critical path steps in a focused table with sequence diagram. |
| `--format <fmt>` | string | Export full journey as `json`, `yaml`, or `mermaid` diagram. |

### 4.3 Dispatch Logic

```
run_journey(args, config):
    journey = build_journey(project_root, config)
    if not journey or not journey.steps:
        print warning "No journey data found. Run mda ingest first."
        return

    if args.step       -> _show_step_detail(journey, step_id)
    elif args.data     -> _show_data_lineage(journey, data_name)
    elif args.format   -> _output_formatted(journey, fmt)
    elif args.critical -> _show_critical_path(journey)
    else               -> _show_journey_summary(journey)
```

### 4.4 Console Output Formats

**Default summary table** (`_show_journey_summary`):

- Header: process name, process ID, total steps.
- Health summary line: avg health, total gaps, steps with job aid.
- Rich table with columns: #, Name, Type, Owner, Inputs, Outputs, Systems, Binding, Health, Gaps.
  - Inputs/Outputs: comma-separated names, truncated to 3 with "+N" overflow.
  - Systems: union of sources and sinks, truncated to 3.
  - Binding: color-coded (green=approved/bound/active, yellow=review, dim=draft, red=other).
  - Health: color-coded (green >= 80, yellow >= 50, red > 0, dim="--" for 0).
- Branch points footer: gateway name with arrow to target names.
- Critical path footer: step names joined with " -> ".

**Step detail** (`_show_step_detail`):

- Rich Panel with capsule ID title.
- Fuzzy matching: if exact capsule_id not found, match by name/ID substring. If ambiguous (multiple matches), list all matches. If no match, print "not found".
- Sections: step number/name, capsule ID, type/owner/binding, health/gaps, preconditions, inputs (with source/required/schema), outputs (with type/sink/invariants), invariants, events emitted, predecessors/successors, external systems (sources/sinks), job aid info (ID/dimensions/rules), gaps (up to 10, with severity).

**Data lineage** (`_show_data_lineage`):

- If data object not found: print available data objects with source and consumer count.
- If found: header with data name, source, consumer list, and ASCII flow diagram: `[Source] -- data_name --> [Consumer1] | [Consumer2]`.

**Critical path** (`_show_critical_path`):

- Header with process name.
- Length line: N steps out of M total.
- Rich table with columns: #, Capsule ID, Name, Type, Owner, Binding.
- Sequence line: step names joined with " -> ".

**Formatted output** (`_output_formatted`):

- `json`: `json.dumps(journey.to_dict(), indent=2)`.
- `yaml`: `yaml.dump()` with `default_flow_style=False, sort_keys=False`. Falls back to JSON if PyYAML not installed.
- `mermaid`: Generates `graph TD` diagram. Gateways use `{}` (diamond) nodes, events use `((""))` (circle) nodes, tasks use `[""]` (rectangle) nodes. Edges connect each step to its successors.

---

## 5. MkDocs Integration

### 5.1 docs_generator.py Integration

In `cli/pipeline/docs_generator.py` (lines 136-167):

1. Import `journey_builder` via `importlib.util` to avoid circular imports.
2. Call `build_journey(project_root, config)`.
3. If journey has steps, set `has_journey = True` and:
   - Create `docs/journey/` directory.
   - Render `journey-index.md.j2` to `docs/journey/index.md` with template context: `process_name`, `steps` (as dicts), `branch_points` (as dicts), `critical_path_ids` (as set), `health_summary`, `mermaid_content`.
   - Render `data-lineage.md.j2` to `docs/journey/data-lineage.md` with template context: `process_name`, `data_lineage` (as dicts).
4. On any exception, set `has_journey = False` (graceful degradation).
5. Pass `has_journey` to `mkdocs.yml.j2` template context (line 289).

### 5.2 journey-index.md.j2

Template: `templates/mkdocs/journey-index.md.j2`

Renders the main journey page with:

- **Health Summary table**: total steps, average health score, grade, steps with gaps, total gaps.
- **Process Flow**: embedded Mermaid diagram (`{{ mermaid_content }}`).
- **Step-by-Step Journey table**: columns #, Step, Type, Owner, Inputs, Outputs, Systems, Binding, Health, Gaps. Steps on the critical path are rendered in **bold**. Step names link to their capsule page (`../{{ step.section }}/{{ step.slug }}/capsule.md`).
- **Decision Points** (conditional on `branch_points`): for each branch point, a sub-heading with condition/target table.

### 5.3 data-lineage.md.j2

Template: `templates/mkdocs/data-lineage.md.j2`

Renders the data lineage page with:

- **Data Objects summary table**: data object name (bold), source, consumers (comma-separated names).
- **Data Flow Details**: for each data object, a section with source (linked to capsule page if not external) and bulleted consumer list with capsule IDs.

### 5.4 mkdocs.yml.j2 Nav Update

In `templates/mkdocs/mkdocs.yml.j2`, the journey section is conditionally included:

```yaml
{%- if has_journey %}
  - Process Journey:
    - Journey Map: journey/index.md
    - Data Lineage: journey/data-lineage.md
{%- endif %}
```

The nav entry appears only when `has_journey` is `True` (journey builder found steps).

---

## 6. Skill

Skill file: `.claude/skills/mda-journey/SKILL.md`

### 6.1 Frontmatter

```yaml
name: mda-journey
description: Show the complete process journey from start to finish. Trace data lineage, see what each step needs and produces, navigate the critical path. Use to understand the full process flow and data dependencies.
argument-hint: [--step <capsule-id>] [--data <data-name>] [--critical-path] [--format yaml|json|mermaid]
allowed-tools: Bash(python *)
```

### 6.2 Usage Patterns

The skill instructs Claude Code to run `python cli/mda.py journey $ARGUMENTS` and explains the common invocations:

| Invocation | Purpose |
|-----------|---------|
| `python cli/mda.py journey` | Full journey table with all steps |
| `python cli/mda.py journey --step CAP-IV-W2V-001` | Single step detail view |
| `python cli/mda.py journey --data borrower_profile` | Trace a data object through lineage |
| `python cli/mda.py journey --critical-path` | Show critical path only |
| `python cli/mda.py journey --format yaml` | Export full journey as YAML |
| `python cli/mda.py journey --format mermaid` | Generate Mermaid diagram |

### 6.3 Interpretation Guidance

The skill directs Claude to explain:

- Step numbers reflect execution order (topological sort).
- Bold steps in the table are on the critical path.
- Inputs/Outputs columns show data dependency counts.
- Systems column shows external API calls.
- Gaps indicate missing knowledge.
- For data lineage, explain origin and consumption chain.

---

## 7. Tests

Test file: `tests/unit/test_journey_builder.py`

Nine tests across five classes:

### 7.1 TestTopologicalSort (4 tests)

| Test | Input | Assertion |
|------|-------|-----------|
| `test_linear_chain` | A->B->C | Result == `["A", "B", "C"]` |
| `test_with_branches` | A->{B,C}->D | First is A, last is D, length is 4 |
| `test_single_node` | A (no edges) | Result == `["A"]` |
| `test_empty` | Empty dict | Result == `[]` |

Helper: `_make_capsule_data(adj)` converts a simple adjacency dict `{"A": ["B"], "B": []}` into capsule_data format with `successor_ids` and `predecessor_ids`.

### 7.2 TestCriticalPath (2 tests)

| Test | Input | Assertion |
|------|-------|-----------|
| `test_linear` | A->B->C (3 StepSummary objects) | Path length 3, path == `["A", "B", "C"]` |
| `test_with_branch` | A->{B,C}->D (4 StepSummary objects) | Path length 3, starts with A, ends with D (either A->B->D or A->C->D) |

### 7.3 TestBuildJourney (1 test)

| Test | Input | Assertion |
|------|-------|-----------|
| `test_income_verification` | `examples/income-verification` fixture | Journey not None, 8 total steps, step_number starts at 1, all capsule IDs populated, process name contains "income" or "verification", critical path non-empty, health summary contains `avg_health` or `avg_score` |

### 7.4 TestDataLineage (1 test)

| Test | Input | Assertion |
|------|-------|-----------|
| `test_income_verification_data` | `examples/income-verification` fixture | `data_lineage` is a list; if non-empty, first entry has `data_name` and `source_name` |

### 7.5 TestBranchPoints (1 test)

| Test | Input | Assertion |
|------|-------|-----------|
| `test_income_verification_branches` | `examples/income-verification` fixture | `branch_points` is a list; if non-empty, first entry has `gateway_name` and at least 2 branches |

---

## 8. Verification

Run these commands from the project root to verify the journey system works end-to-end.

### 8.1 Unit Tests

```bash
python -m pytest tests/unit/test_journey_builder.py -v
```

Expect: 9 tests pass across 5 classes.

### 8.2 CLI Smoke Tests

```bash
# Full journey table
python cli/mda.py journey

# Single step detail (use a capsule ID from your process)
python cli/mda.py journey --step CAP-IV-W2V-001

# Data lineage trace
python cli/mda.py journey --data borrower_profile

# Critical path display
python cli/mda.py journey --critical-path

# Structured export
python cli/mda.py journey --format json
python cli/mda.py journey --format yaml
python cli/mda.py journey --format mermaid
```

All commands should run without errors from an ingested process directory (e.g., `examples/income-verification`).

### 8.3 MkDocs Integration

```bash
# Generate docs (includes journey pages)
python cli/mda.py docs

# Verify generated files exist
ls docs/journey/index.md docs/journey/data-lineage.md

# Serve and inspect in browser
python cli/mda.py docs --serve
```

Verify:

- `docs/journey/index.md` contains the step journey table with critical path bold formatting.
- `docs/journey/data-lineage.md` contains data object source/consumer mappings.
- The MkDocs nav includes "Process Journey" with "Journey Map" and "Data Lineage" sub-items.
