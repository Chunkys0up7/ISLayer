# MDA Intent Layer -- Journey Traceability Specification

*Complete specification for rebuilding the journey traceability system from scratch. Every function, every dataclass field, every template variable, every test assertion.*

## 1. Overview

The journey traceability system traces the start-to-finish process flow of a BPMN-derived MDA process. It reads all triple directories (capsule/intent/contract frontmatter), computes a topological ordering, builds data lineage across steps, identifies branch points at gateway nodes, and computes the critical path (longest path through the DAG). The output is a `ProcessJourney` object that powers CLI display, structured export (JSON/YAML/Mermaid), and MkDocs documentation generation.

Key capabilities:

- **Step ordering** via Kahn's topological sort on the predecessor/successor DAG.
- **Data lineage** mapping every data object from its producer to all consumers.
- **Critical path** computation via longest-path dynamic programming.
- **Branch point detection** at gateway nodes with multiple successors.
- **Health summary** aggregating per-step health scores and gap counts.

### File Inventory

| # | File | Lines | Role |
|---|------|-------|------|
| 1 | `cli/models/journey.py` | 139 | Data model (6 dataclasses) |
| 2 | `cli/pipeline/journey_builder.py` | 595 | Builder algorithm (10-step pipeline) |
| 3 | `cli/commands/journey_cmd.py` | 412 | CLI command and Rich console rendering |
| 4 | `cli/mda.py` | 371 | Argparse registration (lines 177-181) and dispatch (lines 340-343) |
| 5 | `cli/pipeline/docs_generator.py` | 455 | MkDocs integration (lines 136-167, line 289) |
| 6 | `templates/mkdocs/journey-index.md.j2` | 40 | MkDocs journey page Jinja2 template |
| 7 | `templates/mkdocs/data-lineage.md.j2` | 23 | MkDocs data lineage page Jinja2 template |
| 8 | `templates/mkdocs/mkdocs.yml.j2` | (partial) | Conditional nav entry (lines 45-49) |
| 9 | `.claude/skills/mda-journey/SKILL.md` | 40 | Claude Code skill definition |
| 10 | `tests/unit/test_journey_builder.py` | 127 | Unit tests (9 tests, 5 classes) |

---

## 2. Data Model (`cli/models/journey.py`)

All dataclasses live in `cli/models/journey.py`. Every class has a `to_dict()` method for serialization.

### File Header

```python
"""Journey data models — process journey map, step summaries, and data lineage."""
from dataclasses import dataclass, field
from typing import Optional, Any
```

### 2.1 InputSummary

Represents a single input consumed by a step.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `name` | `str` | required | Input data object name |
| `source` | `str` | required | Producing system or capsule |
| `schema_ref` | `Optional[str]` | `None` | Reference to a schema definition |
| `required` | `bool` | `True` | Whether the input is mandatory |

```python
@dataclass
class InputSummary:
    name: str
    source: str
    schema_ref: Optional[str] = None
    required: bool = True

    def to_dict(self):
        return {"name": self.name, "source": self.source, "schema_ref": self.schema_ref, "required": self.required}
```

### 2.2 OutputSummary

Represents a single output produced by a step.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `name` | `str` | required | Output data object name |
| `type` | `str` | required | Data type classification |
| `sink` | `str` | required | Destination system or store |
| `invariants` | `list[str]` | `[]` | Post-conditions that hold after output |

```python
@dataclass
class OutputSummary:
    name: str
    type: str
    sink: str
    invariants: list[str] = field(default_factory=list)

    def to_dict(self):
        return {"name": self.name, "type": self.type, "sink": self.sink, "invariants": self.invariants}
```

### 2.3 StepSummary

The central model representing one step in the journey. Contains all information from capsule, intent, contract, and job aid frontmatter. **23 fields total.**

| # | Field | Type | Default | Description |
|---|-------|------|---------|-------------|
| 1 | `step_number` | `int` | required | Topologically sorted ordinal position (starts at 1) |
| 2 | `capsule_id` | `str` | required | Unique capsule identifier (e.g. `CAP-IV-W2V-001`) |
| 3 | `name` | `str` | required | Human-readable step name |
| 4 | `task_type` | `str` | required | BPMN type: `task`, `gateway`, `event`, etc. |
| 5 | `owner` | `Optional[str]` | required | Role or team responsible |
| 6 | `preconditions` | `list[str]` | `[]` | Conditions that must hold before execution |
| 7 | `required_inputs` | `list[InputSummary]` | `[]` | Data inputs consumed by this step |
| 8 | `predecessor_steps` | `list[str]` | `[]` | Human-readable names of predecessor steps |
| 9 | `outputs` | `list[OutputSummary]` | `[]` | Data outputs produced by this step |
| 10 | `invariants` | `list[str]` | `[]` | Post-conditions that hold after step |
| 11 | `events_emitted` | `list[str]` | `[]` | Domain events fired on completion |
| 12 | `successor_steps` | `list[str]` | `[]` | Human-readable names of successor steps |
| 13 | `sources` | `list[str]` | `[]` | External systems read from |
| 14 | `sinks` | `list[str]` | `[]` | External systems written to |
| 15 | `jobaid_id` | `Optional[str]` | `None` | Associated job aid identifier |
| 16 | `jobaid_dimensions` | `list[str]` | `[]` | Job aid condition dimensions (e.g. loan_program, income_type) |
| 17 | `jobaid_rule_count` | `int` | `0` | Number of rules in the associated job aid |
| 18 | `health_score` | `float` | `0.0` | GAP health score (0-100) |
| 19 | `gaps` | `list[dict]` | `[]` | Gap entries with severity and description |
| 20 | `binding_status` | `str` | `"unknown"` | Triple lifecycle status: draft, review, approved, bound |
| 21 | `slug` | `str` | `""` | URL-safe directory name for docs links |
| 22 | `section` | `str` | `"tasks"` | Either `tasks` or `decisions` |

Note: Field 5 (`owner`) is `Optional[str]` and is positional (no default), so it is required in the constructor signature despite being nullable.

```python
@dataclass
class StepSummary:
    step_number: int
    capsule_id: str
    name: str
    task_type: str
    owner: Optional[str]

    preconditions: list[str] = field(default_factory=list)
    required_inputs: list[InputSummary] = field(default_factory=list)
    predecessor_steps: list[str] = field(default_factory=list)

    outputs: list[OutputSummary] = field(default_factory=list)
    invariants: list[str] = field(default_factory=list)
    events_emitted: list[str] = field(default_factory=list)
    successor_steps: list[str] = field(default_factory=list)

    sources: list[str] = field(default_factory=list)  # External system names
    sinks: list[str] = field(default_factory=list)

    jobaid_id: Optional[str] = None
    jobaid_dimensions: list[str] = field(default_factory=list)
    jobaid_rule_count: int = 0

    health_score: float = 0.0
    gaps: list[dict] = field(default_factory=list)
    binding_status: str = "unknown"

    slug: str = ""
    section: str = "tasks"

    def to_dict(self):
        return {
            "step_number": self.step_number,
            "capsule_id": self.capsule_id,
            "name": self.name,
            "task_type": self.task_type,
            "owner": self.owner,
            "preconditions": self.preconditions,
            "required_inputs": [i.to_dict() for i in self.required_inputs],
            "predecessor_steps": self.predecessor_steps,
            "outputs": [o.to_dict() for o in self.outputs],
            "invariants": self.invariants,
            "events_emitted": self.events_emitted,
            "successor_steps": self.successor_steps,
            "sources": self.sources,
            "sinks": self.sinks,
            "jobaid_id": self.jobaid_id,
            "jobaid_dimensions": self.jobaid_dimensions,
            "jobaid_rule_count": self.jobaid_rule_count,
            "health_score": round(self.health_score, 1),
            "gaps": self.gaps,
            "binding_status": self.binding_status,
            "slug": self.slug,
            "section": self.section,
        }
```

### 2.4 DataLineage

Tracks a single data object from its producer to all consumers.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `data_name` | `str` | required | Data object name |
| `source` | `str` | required | `"external"` or a capsule_id |
| `source_name` | `str` | required | Human-readable producer name |
| `consumers` | `list[dict]` | `[]` | List of `{capsule_id, name}` consumer entries |

```python
@dataclass
class DataLineage:
    data_name: str
    source: str  # "external" or capsule_id
    source_name: str  # human-readable
    consumers: list[dict] = field(default_factory=list)  # [{capsule_id, name}]

    def to_dict(self):
        return {"data_name": self.data_name, "source": self.source, "source_name": self.source_name, "consumers": self.consumers}
```

### 2.5 BranchPoint

Represents a decision gateway where the process flow diverges.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `gateway_capsule_id` | `str` | required | Capsule ID of the gateway step |
| `gateway_name` | `str` | required | Human-readable gateway name |
| `branches` | `list[dict]` | `[]` | List of `{condition, target_capsule_id, target_name}` |

```python
@dataclass
class BranchPoint:
    gateway_capsule_id: str
    gateway_name: str
    branches: list[dict] = field(default_factory=list)  # [{condition, target_capsule_id, target_name}]

    def to_dict(self):
        return {"gateway_capsule_id": self.gateway_capsule_id, "gateway_name": self.gateway_name, "branches": self.branches}
```

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
| `health_summary` | `dict` | `{}` | Aggregate health: avg_health, total_gaps, steps_with_jobaid, etc. |

```python
@dataclass
class ProcessJourney:
    process_name: str
    process_id: str
    total_steps: int
    steps: list[StepSummary] = field(default_factory=list)
    data_lineage: list[DataLineage] = field(default_factory=list)
    critical_path: list[str] = field(default_factory=list)
    branch_points: list[BranchPoint] = field(default_factory=list)
    health_summary: dict = field(default_factory=dict)

    def get_step(self, capsule_id: str) -> Optional[StepSummary]:
        for s in self.steps:
            if s.capsule_id == capsule_id:
                return s
        return None

    def get_data(self, data_name: str) -> Optional[DataLineage]:
        name_lower = data_name.lower().replace("-", "_").replace(" ", "_")
        for dl in self.data_lineage:
            if dl.data_name.lower().replace("-", "_").replace(" ", "_") == name_lower:
                return dl
        return None

    def to_dict(self):
        return {
            "process_name": self.process_name,
            "process_id": self.process_id,
            "total_steps": self.total_steps,
            "steps": [s.to_dict() for s in self.steps],
            "data_lineage": [dl.to_dict() for dl in self.data_lineage],
            "critical_path": self.critical_path,
            "branch_points": [bp.to_dict() for bp in self.branch_points],
            "health_summary": self.health_summary,
        }
```

Helper methods:

- `get_step(capsule_id)` -- Linear scan lookup by exact capsule ID. Returns `Optional[StepSummary]`.
- `get_data(data_name)` -- Normalized fuzzy lookup. Lowercases the query, replaces hyphens and spaces with underscores, then compares against each `DataLineage.data_name` with the same normalization. Returns `Optional[DataLineage]`.

---

## 3. Journey Builder (`cli/pipeline/journey_builder.py`)

### 3.0 Import Pattern and Module Loading

The builder uses `importlib.util` to load `mda_io` modules (`frontmatter` and `yaml_io`) because they live outside the standard package path. This pattern avoids circular imports and works from both CLI and test contexts.

```python
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
```

The `_load_io(name)` function:
1. Computes the path: `cli/mda_io/{name}.py` (two directories up from `cli/pipeline/` to reach `cli/`, then into `mda_io/`).
2. Creates a module spec from the file location.
3. Creates a module object and executes it.
4. Returns the loaded module.

This is called at module level for `frontmatter` and `yaml_io`. These modules provide:
- `frontmatter_mod.read_frontmatter_file(path)` -- Returns `(dict, str)` tuple of (frontmatter dict, body text).
- `yaml_io.read_yaml(path)` -- Returns parsed YAML as a dict.

### 3.1 `build_journey()` -- The 10-Step Algorithm

```python
def build_journey(project_root: Path, config) -> Optional[ProcessJourney]:
```

**Parameters:**
- `project_root` -- `Path` to the process repository root.
- `config` -- Config object with `.get(key, default)` method. Expected keys: `paths.triples`, `output.triples_dir`, `paths.decisions`, `output.decisions_dir`, `process.id`, `process.name`, `paths.output`, `output.output_dir`.

**Returns:** `Optional[ProcessJourney]` -- `None` if no triple directories or no capsule data found.

**The 10 Steps:**

**Step 1: Resolve paths.**

```python
triples_path = config.get("paths.triples") or config.get("output.triples_dir") or "triples"
decisions_path = config.get("paths.decisions") or config.get("output.decisions_dir") or "decisions"
triples_dir = project_root / triples_path
decisions_dir = project_root / decisions_path

process_id = config.get("process.id", "unknown")
process_name = config.get("process.name", project_root.name.replace("-", " ").title())
```

**Step 2: Discover triple directories.**

```python
triple_dirs = _discover_triple_dirs(triples_dir, decisions_dir)
if not triple_dirs:
    return None
```

**Step 3: Read capsule data for each triple directory.**

```python
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
```

**Step 4: Read process-graph.yaml for data_objects.**

```python
graph_data = _read_graph_data(project_root, config)
```

**Step 5: Topological sort.**

```python
sorted_ids = topological_sort(capsule_data)
```

**Step 6: Build StepSummary for each in sorted order.**

```python
steps = []
for step_num, cid in enumerate(sorted_ids, start=1):
    cd = capsule_data[cid]
    step = _build_step_summary(step_num, cid, cd, capsule_names)
    steps.append(step)
```

**Step 7: Build DataLineage.**

```python
data_lineage = build_data_lineage(graph_data, capsule_data, capsule_names)
```

**Step 8: Detect branch points.**

```python
branch_points = detect_branch_points(steps, capsule_data)
```

**Step 9: Compute critical path.**

```python
critical_path = compute_critical_path(steps, capsule_data)
```

**Step 10: Compute health summary and assemble result.**

```python
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
```

### 3.2 `_discover_triple_dirs(triples_dir, decisions_dir)`

```python
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
```

Logic:
1. Iterates `triples_dir` (section="tasks") then `decisions_dir` (section="decisions").
2. Skips directories starting with `_`.
3. Only includes directories containing at least one `*.cap.md` file.
4. Directories are sorted alphabetically within each base.
5. Returns list of `(Path, str)` tuples.

### 3.3 `_read_triple_dir(triple_dir, section)`

```python
def _read_triple_dir(triple_dir: Path, section: str) -> dict:
```

Reads capsule, intent, contract frontmatter and job aid data from a single triple directory.

**Returns:** A dict with the following keys:

| Key | Source | Fallback |
|-----|--------|----------|
| `section` | Parameter | -- |
| `slug` | `triple_dir.name` | -- |
| `dir` | `triple_dir` | -- |
| `capsule_id` | `cap_fm["capsule_id"]` | `""` |
| `name` | `cap_fm["bpmn_task_name"]` | `triple_dir.name` |
| `task_type` | `cap_fm["bpmn_task_type"]` | `"unknown"` |
| `owner` | `cap_fm["owner_role"]` | `None` |
| `status` | `cap_fm["status"]` | `"draft"` |
| `predecessor_ids` | `cap_fm["predecessor_ids"]` | `[]` |
| `successor_ids` | `cap_fm["successor_ids"]` | `[]` |
| `bpmn_task_id` | `cap_fm["bpmn_task_id"]` | `""` |
| `binding_status` | `cap_fm["binding_status"]` or `cap_fm["status"]` | `"unknown"` |
| `intent_fm` | Full intent frontmatter dict | `{}` |
| `intent_inputs` | `int_fm["required_inputs"]` | `[]` |
| `intent_outputs` | `int_fm["outputs"]` | `[]` |
| `preconditions` | `int_fm["preconditions"]` | `[]` |
| `invariants` | `int_fm["invariants"]` | `[]` |
| `events_emitted` | `int_fm["events_emitted"]` or `int_fm["domain_events"]` | `[]` |
| `sources` | `int_fm["source_systems"]` | `[]` |
| `sinks` | `int_fm["target_systems"]` or `int_fm["sink_systems"]` | `[]` |
| `contract_fm` | Full contract frontmatter dict | `{}` |
| `jobaid_id` | `ja_data["jobaid_id"]` or file stem | `None` |
| `jobaid_dimensions` | keys of `ja_data["dimensions"]` dict | `[]` |
| `jobaid_rule_count` | `len(ja_data["rules"])` | `0` |
| `health_score` | -- | `0.0` |
| `gaps` | -- | `[]` |

**File glob patterns:**
- Capsule: `*.cap.md`
- Intent: `*.int.md`
- Contract: `*.ict.md`
- Job Aid: `*.jobaid.yaml`

```python
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
```

### 3.4 `_read_graph_data(project_root, config)`

```python
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
```

Searches for `process-graph.yaml` in two locations:
1. Project root directly.
2. Output directory (from config `paths.output` or `output.output_dir`, falling back to `"output"`).

### 3.5 `topological_sort(capsule_data)`

```python
def topological_sort(capsule_data: dict) -> list[str]:
```

Implements Kahn's algorithm for topological sorting.

**Input format:** `dict[str, dict]` where each value has `"successor_ids"` and `"predecessor_ids"` keys (both lists of capsule ID strings).

**Algorithm:**

1. **Build structures** -- Create `adj` dict (capsule_id -> list of successor IDs within the known set) and `in_degree` counter for all capsule IDs. Only edges where both endpoints are in `capsule_data` are included.
2. **Initialize queue** -- Collect all nodes with `in_degree == 0`. Sort alphabetically for deterministic output. Use `collections.deque`.
3. **Process queue** -- Dequeue a node, append to `result`. For each successor (processed in sorted order): decrement `in_degree`. When a successor reaches `in_degree == 0`, append to queue.
4. **Cycle handling** -- After the queue is exhausted, any nodes not in `result` form cycles. These are appended to the result in sorted order. A `warnings.warn()` is emitted listing up to 5 cycle participants.

```python
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
```

**Returns:** Ordered list of capsule ID strings.

### 3.6 `compute_critical_path(steps, capsule_data)`

```python
def compute_critical_path(steps: list[StepSummary], capsule_data: dict) -> list[str]:
```

Longest-path dynamic programming on the topologically sorted step order.

**Algorithm:**

1. **Build maps** -- Create `pred_map` (capsule_id -> predecessor IDs within the step set) and `succ_map` (capsule_id -> successor IDs within the step set) from `capsule_data`.
2. **Initialize DP** -- `longest_to[cid] = 1` for all nodes. `prev_on_path[cid] = None` for backtracking.
3. **Forward pass** -- For each node in step order (already topologically sorted), for each predecessor: if `longest_to[pred] + 1 > longest_to[cid]`, update `longest_to[cid]` and record `prev_on_path[cid] = pred`.
4. **Find end node** -- The node with the maximum `longest_to` value (using `max(..., key=longest_to.get)`).
5. **Backtrack** -- Follow `prev_on_path` chain from end node back to a node with `prev_on_path == None`. Reverse the collected path.

```python
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
```

**Returns:** Ordered list of capsule IDs forming the longest path through the DAG.

### 3.7 `build_data_lineage(graph_data, capsule_data, capsule_names)`

```python
def build_data_lineage(
    graph_data: dict, capsule_data: dict, capsule_names: dict
) -> list[DataLineage]:
```

Two-phase approach with primary and fallback sources.

**Phase 1 -- From process-graph.yaml data_objects (primary):**

Expected graph data format:
```yaml
data_objects:
  - id: borrower_profile
    produced_by: Task_ReceiveRequest  # BPMN task ID or "external"
    consumed_by: [Task_ClassifyEmployment, Task_VerifyW2]
```

1. Build `bpmn_to_capsule` mapping from capsule frontmatter `bpmn_task_id` field.
2. For each entry in `graph_data["data_objects"]` (must be a list of dicts):
   - `produced_by`: if `"external"`, source is `"external"` with name `"External System"`; otherwise map BPMN task ID to capsule ID via `bpmn_to_capsule`.
   - `consumed_by`: map each BPMN task ID to capsule ID, build consumer list of `{"capsule_id": ..., "name": ...}`.
   - Create `DataLineage` record. Track seen data names (normalized: lowercase, hyphens/spaces to underscores) in `seen_data` set.

**Phase 2 -- Fallback from intent inputs/outputs (only if Phase 1 yields zero items):**

1. Collect all outputs from intent frontmatter: `output_producers[normalized_name] = (capsule_id, name)`. Inputs can be dicts with a `"name"` key or plain strings.
2. Collect all inputs: `input_consumers[normalized_name] = [{capsule_id, name}, ...]`.
3. Union all data names from both maps.
4. For each name (sorted): if it appears in `output_producers`, that capsule is the source; otherwise source is `"external"` / `"External System"`. Consumers come from `input_consumers`.
5. Data name display: `dname.replace("_", " ").title()` (title-cased with underscores to spaces).

**Normalization:** `name.lower().replace("-", "_").replace(" ", "_")`

```python
def build_data_lineage(
    graph_data: dict, capsule_data: dict, capsule_names: dict
) -> list[DataLineage]:
    """Build data lineage from process-graph.yaml data_objects and intent inputs/outputs."""
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
        input_consumers = {}  # normalized_name -> list of {capsule_id, name}
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
```

### 3.8 `detect_branch_points(steps, capsule_data)`

```python
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
```

Logic:
1. Build `step_names` lookup from step list (capsule_id -> name).
2. For each step, check `capsule_data[capsule_id]["successor_ids"]`.
3. If a step has more than one successor, create a `BranchPoint` with one branch entry per successor.
4. Condition is always left as empty string (would require edge-level data from the BPMN model).

### 3.9 `_build_step_summary(step_number, capsule_id, cd, capsule_names)`

```python
def _build_step_summary(
    step_number: int, capsule_id: str, cd: dict, capsule_names: dict
) -> StepSummary:
```

Constructs a `StepSummary` from a capsule data dict.

**Input parsing:**
- Inputs (`cd["intent_inputs"]`): Each item can be a `dict` (with `name`, `source`, `schema_ref`/`schema`, `required` keys) or a `str` (becomes `InputSummary(name=str, source="unknown")`).
- Outputs (`cd["intent_outputs"]`): Each item can be a `dict` (with `name`, `type`, `sink`, `invariants` keys) or a `str` (becomes `OutputSummary(name=str, type="unknown", sink="")`).
- Predecessor/successor steps are resolved to human-readable names via `capsule_names` dict.

```python
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
```

### 3.10 `_compute_health_summary(steps)`

```python
def _compute_health_summary(steps: list[StepSummary]) -> dict:
```

Computes aggregate health metrics.

**Empty case:** Returns `{"total_steps": 0, "avg_health": 0.0, "steps_with_gaps": 0, "total_gaps": 0}`.

**Normal case:** Returns dict with keys:

| Key | Computation |
|-----|-------------|
| `total_steps` | `len(steps)` |
| `avg_health` | Mean of non-zero `health_score` values, rounded to 1 decimal. 0.0 if all zero. |
| `steps_with_gaps` | Count of steps where `s.gaps` is non-empty |
| `total_gaps` | Sum of `len(s.gaps)` across all steps |
| `binding_counts` | Dict with `bound` (approved/bound/active), `draft`, `review` (review/in_review) counts |
| `steps_with_jobaid` | Count of steps where `s.jobaid_id` is truthy |
| `total_inputs` | Sum of `len(s.required_inputs)` |
| `total_outputs` | Sum of `len(s.outputs)` |
| `total_events` | Sum of `len(s.events_emitted)` |

```python
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
```

---

## 4. CLI Command (`cli/commands/journey_cmd.py`)

### 4.1 Argparse Registration (in `cli/mda.py`)

```python
# --- Journey Traceability ---
journey_parser = subparsers.add_parser("journey", help="Process journey traceability: steps, data lineage, critical path")
journey_parser.add_argument("--step", help="Show detail for a specific step (capsule ID or name substring)")
journey_parser.add_argument("--data", help="Show data lineage for a specific data object")
journey_parser.add_argument("--format", choices=["json", "yaml", "mermaid"], help="Output in structured format")
journey_parser.add_argument("--critical-path", action="store_true", help="Show only the critical path")
```

Dispatch (in `cli/mda.py`):

```python
elif args.command == "journey":
    from commands.journey_cmd import run_journey

    run_journey(args, config)
```

### 4.2 Entry Point

```python
"""mda journey — Display process journey traceability: step summaries, data lineage, critical path."""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def run_journey(args, config):
    """Entry point for the mda journey command."""
    from pipeline.journey_builder import build_journey
    from output.console import console, print_header, print_info, print_table, print_warning
    from output.json_output import output_json

    project_root = config.project_root
    journey = build_journey(project_root, config)

    if not journey or not journey.steps:
        print_warning("No journey data found. Run mda ingest first.")
        return

    step_id = getattr(args, "step", None)
    data_name = getattr(args, "data", None)
    fmt = getattr(args, "format", None)
    critical = getattr(args, "critical_path", False)

    if step_id:
        _show_step_detail(journey, step_id)
    elif data_name:
        _show_data_lineage(journey, data_name)
    elif fmt:
        _output_formatted(journey, fmt)
    elif critical:
        _show_critical_path(journey)
    else:
        _show_journey_summary(journey)
```

### 4.3 Five Display Modes

#### Mode 1: `_show_journey_summary(journey)`

Default view. Uses Rich `Table` with `box.SIMPLE_HEAVY` and `show_lines=True`.

**Header:** Process name, process ID, total steps.
**Health line:** Avg health, total gaps, steps with job aid.

**Table columns:** `#` (dim, width=4), `Name` (bold), `Type` (dim), `Owner`, `Inputs` (width=14), `Outputs` (width=14), `Systems`, `Binding` (width=10), `Health` (width=8), `Gaps` (width=6).

**Column rendering:**
- Inputs: comma-joined first 3 input names, then ` +N` if more.
- Outputs: comma-joined first 3 output names, then ` +N` if more.
- Systems: `sorted(set(step.sources + step.sinks))`, first 3, then ` +N`.
- Binding: color-coded Rich markup: green=approved/bound/active, yellow=review/in_review, dim=draft, red=anything else.
- Health: green >= 80, yellow >= 50, red > 0, dim="--" for 0.
- Gaps: count if nonzero, dim "0" otherwise.

**Footer sections:**
- Branch points: `{gateway_name} -> {target_names joined by comma}` for each.
- Critical path: `{step_names joined by " -> "}` with length count.

```python
def _show_journey_summary(journey):
    """Print the full journey as a Rich table."""
    from output.console import console, print_header
    from rich.table import Table
    from rich import box

    print_header(f"Process Journey: {journey.process_name}")
    console.print(f"  Process ID: [bold]{journey.process_id}[/bold]  |  Steps: [bold]{journey.total_steps}[/bold]")

    hs = journey.health_summary
    if hs:
        console.print(
            f"  Avg Health: [bold]{hs.get('avg_health', 0)}[/bold]  |  "
            f"Gaps: [bold]{hs.get('total_gaps', 0)}[/bold]  |  "
            f"With Job Aid: [bold]{hs.get('steps_with_jobaid', 0)}[/bold]"
        )
    console.print()

    table = Table(title="Step Journey Map", box=box.SIMPLE_HEAVY, show_lines=True)
    table.add_column("#", style="dim", width=4)
    table.add_column("Name", style="bold")
    table.add_column("Type", style="dim")
    table.add_column("Owner")
    table.add_column("Inputs", width=14)
    table.add_column("Outputs", width=14)
    table.add_column("Systems")
    table.add_column("Binding", width=10)
    table.add_column("Health", width=8)
    table.add_column("Gaps", width=6)

    for step in journey.steps:
        inputs_str = ", ".join(i.name for i in step.required_inputs[:3])
        if len(step.required_inputs) > 3:
            inputs_str += f" +{len(step.required_inputs) - 3}"

        outputs_str = ", ".join(o.name for o in step.outputs[:3])
        if len(step.outputs) > 3:
            outputs_str += f" +{len(step.outputs) - 3}"

        systems = sorted(set(step.sources + step.sinks))
        systems_str = ", ".join(systems[:3])
        if len(systems) > 3:
            systems_str += f" +{len(systems) - 3}"

        binding_color = {
            "approved": "green", "bound": "green", "active": "green",
            "review": "yellow", "in_review": "yellow",
            "draft": "dim",
        }.get(step.binding_status, "red")
        binding_str = f"[{binding_color}]{step.binding_status}[/{binding_color}]"

        health_val = step.health_score
        if health_val >= 80:
            health_str = f"[green]{health_val}[/green]"
        elif health_val >= 50:
            health_str = f"[yellow]{health_val}[/yellow]"
        elif health_val > 0:
            health_str = f"[red]{health_val}[/red]"
        else:
            health_str = "[dim]--[/dim]"

        gaps_str = str(len(step.gaps)) if step.gaps else "[dim]0[/dim]"

        table.add_row(
            str(step.step_number),
            step.name,
            step.task_type,
            step.owner or "[dim]--[/dim]",
            inputs_str or "[dim]--[/dim]",
            outputs_str or "[dim]--[/dim]",
            systems_str or "[dim]--[/dim]",
            binding_str,
            health_str,
            gaps_str,
        )

    console.print(table)

    # Branch points
    if journey.branch_points:
        console.print(f"\n[bold]Branch Points:[/bold] {len(journey.branch_points)}")
        for bp in journey.branch_points:
            targets = ", ".join(b.get("target_name", "?") for b in bp.branches)
            console.print(f"  {bp.gateway_name} -> {targets}")

    # Critical path
    if journey.critical_path:
        path_names = []
        for cid in journey.critical_path:
            step = journey.get_step(cid)
            path_names.append(step.name if step else cid)
        console.print(f"\n[bold]Critical Path ({len(journey.critical_path)} steps):[/bold]")
        console.print("  " + " -> ".join(path_names))
```

#### Mode 2: `_show_step_detail(journey, step_id)`

Detailed view of a single step in a Rich Panel.

**Fuzzy matching:** If exact `capsule_id` not found, searches all steps for `step_id.lower()` in `s.name.lower()` or `s.capsule_id.lower()`. If 1 match, uses it. If multiple matches, lists all. If no match, prints "not found".

**Panel content sections:**
1. Step number and name (bold)
2. Capsule ID
3. Type | Owner | Binding
4. Health Score | Gaps count
5. Preconditions (bulleted list, if any)
6. Inputs with count, each showing source, required/optional, schema_ref
7. Outputs with count, each showing type, sink, invariants
8. Invariants (bulleted list, if any)
9. Events Emitted (bulleted list, if any)
10. Predecessors (comma-joined)
11. Successors (comma-joined)
12. External Systems: Sources and Sinks
13. Job Aid: ID, dimensions, rule count
14. Gaps (up to 10): severity and description/message

```python
def _show_step_detail(journey, step_id):
    """Show detailed view of a single step."""
    from output.console import console, print_header, print_warning
    from rich.panel import Panel
    from rich.table import Table
    from rich import box

    step = journey.get_step(step_id)
    if not step:
        # Try matching by name substring
        matches = [s for s in journey.steps if step_id.lower() in s.name.lower() or step_id.lower() in s.capsule_id.lower()]
        if len(matches) == 1:
            step = matches[0]
        elif matches:
            print_warning(f"Ambiguous step ID '{step_id}'. Matches:")
            for m in matches:
                console.print(f"  {m.capsule_id}  {m.name}")
            return
        else:
            print_warning(f"Step '{step_id}' not found.")
            return

    lines = []
    lines.append(f"[bold]Step {step.step_number}:[/bold] {step.name}")
    lines.append(f"Capsule ID: {step.capsule_id}")
    lines.append(f"Type: {step.task_type}  |  Owner: {step.owner or '--'}  |  Binding: {step.binding_status}")
    lines.append(f"Health Score: {step.health_score}  |  Gaps: {len(step.gaps)}")

    if step.preconditions:
        lines.append(f"\n[bold]Preconditions:[/bold]")
        for pc in step.preconditions:
            lines.append(f"  - {pc}")

    if step.required_inputs:
        lines.append(f"\n[bold]Inputs ({len(step.required_inputs)}):[/bold]")
        for inp in step.required_inputs:
            req = "required" if inp.required else "optional"
            schema = f"  schema: {inp.schema_ref}" if inp.schema_ref else ""
            lines.append(f"  - {inp.name}  (source: {inp.source}, {req}){schema}")

    if step.outputs:
        lines.append(f"\n[bold]Outputs ({len(step.outputs)}):[/bold]")
        for out in step.outputs:
            inv = f"  invariants: {', '.join(out.invariants)}" if out.invariants else ""
            lines.append(f"  - {out.name}  (type: {out.type}, sink: {out.sink}){inv}")

    if step.invariants:
        lines.append(f"\n[bold]Invariants:[/bold]")
        for inv in step.invariants:
            lines.append(f"  - {inv}")

    if step.events_emitted:
        lines.append(f"\n[bold]Events Emitted:[/bold]")
        for ev in step.events_emitted:
            lines.append(f"  - {ev}")

    if step.predecessor_steps:
        lines.append(f"\n[bold]Predecessors:[/bold] {', '.join(step.predecessor_steps)}")
    if step.successor_steps:
        lines.append(f"[bold]Successors:[/bold] {', '.join(step.successor_steps)}")

    if step.sources or step.sinks:
        lines.append(f"\n[bold]External Systems:[/bold]")
        if step.sources:
            lines.append(f"  Sources: {', '.join(step.sources)}")
        if step.sinks:
            lines.append(f"  Sinks: {', '.join(step.sinks)}")

    if step.jobaid_id:
        lines.append(f"\n[bold]Job Aid:[/bold] {step.jobaid_id}")
        lines.append(f"  Dimensions: {', '.join(step.jobaid_dimensions) if step.jobaid_dimensions else '--'}")
        lines.append(f"  Rules: {step.jobaid_rule_count}")

    if step.gaps:
        lines.append(f"\n[bold]Gaps ({len(step.gaps)}):[/bold]")
        for gap in step.gaps[:10]:
            sev = gap.get("severity", "?")
            desc = gap.get("description", gap.get("message", str(gap)))
            lines.append(f"  [{sev}] {desc}")

    console.print(Panel("\n".join(lines), title=f"Step Detail: {step.capsule_id}", border_style="blue"))
```

#### Mode 3: `_show_data_lineage(journey, data_name)`

Traces a single data object through its lineage.

- Uses `journey.get_data(data_name)` for fuzzy lookup.
- If not found: prints warning and lists all available data objects with source and consumer count.
- If found: shows source, consumer list, and ASCII flow diagram.

**Flow diagram format:** `[Source Name] -- data_name --> [Consumer1] | [Consumer2]`

```python
def _show_data_lineage(journey, data_name):
    """Show data lineage for a specific data object."""
    from output.console import console, print_header, print_warning

    dl = journey.get_data(data_name)
    if not dl:
        print_warning(f"Data object '{data_name}' not found.")
        if journey.data_lineage:
            console.print("\n[bold]Available data objects:[/bold]")
            for d in journey.data_lineage:
                console.print(f"  {d.data_name}  (source: {d.source_name}, consumers: {len(d.consumers)})")
        return

    print_header(f"Data Lineage: {dl.data_name}")
    console.print(f"  Source: [bold]{dl.source_name}[/bold] ({dl.source})")

    if dl.consumers:
        console.print(f"\n  [bold]Consumed by ({len(dl.consumers)}):[/bold]")
        for c in dl.consumers:
            console.print(f"    -> {c.get('name', '?')}  ({c.get('capsule_id', '?')})")
    else:
        console.print("  [dim]No consumers found.[/dim]")

    # Show flow diagram
    console.print(f"\n  [bold]Flow:[/bold]")
    flow_parts = [f"[{dl.source_name}]"]
    flow_parts.append(f" -- {dl.data_name} -->")
    if dl.consumers:
        consumer_names = [c.get("name", "?") for c in dl.consumers]
        flow_parts.append(" | ".join(f"[{n}]" for n in consumer_names))
    else:
        flow_parts.append("[no consumers]")
    console.print("  " + " ".join(flow_parts))
```

#### Mode 4: `_show_critical_path(journey)`

Filtered view of critical path steps.

- Header with process name.
- Length line: `N steps out of M total`.
- Rich Table with `box.SIMPLE_HEAVY`: columns `#`, `Capsule ID`, `Name` (bold), `Type`, `Owner`, `Binding`.
- Only includes steps whose `capsule_id` is in `journey.critical_path`.
- Sequence line: step names joined with ` -> `.

```python
def _show_critical_path(journey):
    """Highlight critical path steps."""
    from output.console import console, print_header
    from rich.table import Table
    from rich import box

    print_header(f"Critical Path: {journey.process_name}")

    if not journey.critical_path:
        console.print("  [dim]No critical path computed (no predecessor/successor data).[/dim]")
        return

    console.print(f"  Length: [bold]{len(journey.critical_path)}[/bold] steps out of {journey.total_steps} total\n")

    table = Table(title="Critical Path Steps", box=box.SIMPLE_HEAVY)
    table.add_column("#", style="dim", width=4)
    table.add_column("Capsule ID")
    table.add_column("Name", style="bold")
    table.add_column("Type")
    table.add_column("Owner")
    table.add_column("Binding")

    cp_set = set(journey.critical_path)
    for step in journey.steps:
        if step.capsule_id in cp_set:
            table.add_row(
                str(step.step_number),
                step.capsule_id,
                step.name,
                step.task_type,
                step.owner or "--",
                step.binding_status,
            )

    console.print(table)

    # Path sequence
    path_names = []
    for cid in journey.critical_path:
        step = journey.get_step(cid)
        path_names.append(step.name if step else cid)
    console.print(f"\n[bold]Sequence:[/bold]")
    console.print("  " + " -> ".join(path_names))
```

#### Mode 5: `_output_formatted(journey, fmt)`

Structured export.

```python
def _output_formatted(journey, fmt):
    """Output journey in a structured format."""
    from output.console import console

    data = journey.to_dict()

    if fmt == "json":
        import json
        print(json.dumps(data, indent=2, default=str))

    elif fmt == "yaml":
        try:
            import yaml
            print(yaml.dump(data, default_flow_style=False, sort_keys=False))
        except ImportError:
            from output.json_output import output_json
            output_json(data)

    elif fmt == "mermaid":
        _print_mermaid(journey)

    else:
        import json
        print(json.dumps(data, indent=2, default=str))
```

### 4.4 Mermaid Output (`_print_mermaid`)

```python
def _print_mermaid(journey):
    """Generate a Mermaid diagram with data flow annotations."""
    lines = ["graph TD"]

    # Nodes
    for step in journey.steps:
        nid = step.capsule_id.replace("-", "_")
        label = step.name
        if "gateway" in step.task_type.lower() or "Gateway" in step.task_type:
            lines.append(f'    {nid}{{{{{label}}}}}')
        elif "event" in step.task_type.lower() or "Event" in step.task_type:
            lines.append(f'    {nid}(("{label}"))')
        else:
            lines.append(f'    {nid}["{label}"]')

    # Edges from successor relationships
    seen_edges = set()
    for step in journey.steps:
        for succ_name in step.successor_steps:
            # Find the successor step by name
            succ_step = None
            for s in journey.steps:
                if s.name == succ_name or s.capsule_id == succ_name:
                    succ_step = s
                    break
            if succ_step:
                edge_key = (step.capsule_id, succ_step.capsule_id)
                if edge_key not in seen_edges:
                    src = step.capsule_id.replace("-", "_")
                    tgt = succ_step.capsule_id.replace("-", "_")
                    lines.append(f'    {src} --> {tgt}')
                    seen_edges.add(edge_key)

    # Data flow annotations as comments
    if journey.data_lineage:
        lines.append("")
        lines.append("    %% Data Flow")
        for dl in journey.data_lineage:
            src = dl.source.replace("-", "_") if dl.source != "external" else "ext"
            for c in dl.consumers:
                tgt = c.get("capsule_id", "").replace("-", "_")
                if src and tgt:
                    lines.append(f'    %% {dl.data_name}: {src} -> {tgt}')

    # Style
    lines.append("")
    lines.append("    classDef task fill:#e1f5fe,stroke:#01579b")
    lines.append("    classDef gateway fill:#fff3e0,stroke:#e65100")
    lines.append("    classDef event fill:#e8f5e9,stroke:#1b5e20")
    lines.append("    classDef critical fill:#ffcdd2,stroke:#b71c1c")

    cp_set = set(journey.critical_path)
    for step in journey.steps:
        nid = step.capsule_id.replace("-", "_")
        if step.capsule_id in cp_set:
            lines.append(f"    class {nid} critical")
        elif "gateway" in step.task_type.lower() or "Gateway" in step.task_type:
            lines.append(f"    class {nid} gateway")
        elif "event" in step.task_type.lower() or "Event" in step.task_type:
            lines.append(f"    class {nid} event")
        else:
            lines.append(f"    class {nid} task")

    print("\n".join(lines))
```

**Node shapes:**
- Gateway (`"gateway"` or `"Gateway"` in task_type): `{nid}{{{label}}}` (diamond)
- Event (`"event"` or `"Event"` in task_type): `{nid}(("{label}"))` (circle)
- Task (everything else): `{nid}["{label}"]` (rectangle)

**Edge resolution:** Successors are stored as human-readable names. The code searches all steps to find a match by `s.name == succ_name` or `s.capsule_id == succ_name`. Deduplication via `seen_edges` set.

**Style classes:**
- `task`: `fill:#e1f5fe,stroke:#01579b` (light blue)
- `gateway`: `fill:#fff3e0,stroke:#e65100` (orange)
- `event`: `fill:#e8f5e9,stroke:#1b5e20` (green)
- `critical`: `fill:#ffcdd2,stroke:#b71c1c` (red, overrides other types on critical path)

**Data flow annotations:** Added as Mermaid comments (`%%`) showing `data_name: source_id -> consumer_id`.

---

## 5. MkDocs Integration

### 5.1 `docs_generator.py` Integration

In `cli/pipeline/docs_generator.py` (lines 136-167):

```python
# Generate docs/journey/
has_journey = False
try:
    import importlib.util as _ilu
    _jb_spec = _ilu.spec_from_file_location("journey_builder",
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "journey_builder.py"))
    _jb_mod = _ilu.module_from_spec(_jb_spec)
    _jb_spec.loader.exec_module(_jb_mod)

    journey = _jb_mod.build_journey(project_root, config)
    if journey and journey.steps:
        has_journey = True
        journey_dir = docs_dir / "journey"
        journey_dir.mkdir()

        critical_path_ids = set(journey.critical_path)

        _render_template(env, "journey-index.md.j2", journey_dir / "index.md", {
            "process_name": process_name,
            "steps": [s.to_dict() for s in journey.steps],
            "branch_points": [bp.to_dict() for bp in journey.branch_points],
            "critical_path_ids": critical_path_ids,
            "health_summary": journey.health_summary,
            "mermaid_content": mermaid_content,
        })

        _render_template(env, "data-lineage.md.j2", journey_dir / "data-lineage.md", {
            "process_name": process_name,
            "data_lineage": [dl.to_dict() for dl in journey.data_lineage],
        })
except Exception:
    has_journey = False
```

And at line 289, `has_journey` is passed to the mkdocs.yml.j2 template:

```python
_render_template(env, "mkdocs.yml.j2", project_root / "mkdocs.yml", {
    "process_name": process_name,
    "site_name": f"{process_name} — MDA Intent Layer",
    "nav_tasks": nav_tasks,
    "nav_decisions": nav_decisions,
    "has_journey": has_journey,
    "has_corpus": bool(corpus_sections),
    "corpus_sections": corpus_sections,
})
```

Key details:
- Uses `importlib.util` to load `journey_builder.py` from the same directory (`cli/pipeline/`).
- Steps and branch_points are serialized to dicts via `.to_dict()` before passing to templates.
- `critical_path_ids` is a Python `set` (for `in` operator in Jinja2 templates).
- `mermaid_content` is a pre-generated string from the graph builder (shared with flow/diagram.md).
- On any exception, gracefully degrades: `has_journey = False`.
- Output files: `docs/journey/index.md` and `docs/journey/data-lineage.md`.

### 5.2 `journey-index.md.j2` Template

**File:** `templates/mkdocs/journey-index.md.j2`

**Template variables:**
- `process_name` (str)
- `steps` (list of dicts, each from `StepSummary.to_dict()`)
- `branch_points` (list of dicts, each from `BranchPoint.to_dict()`)
- `critical_path_ids` (set of capsule ID strings)
- `health_summary` (dict with `avg_score`, `grade`, `steps_with_gaps`, `total_gaps`)
- `mermaid_content` (str, raw Mermaid diagram text)

**Complete template:**

```jinja2
# Journey Map: {{ process_name }}

## Health Summary

| Metric | Value |
|--------|-------|
| Total Steps | {{ steps|length }} |
| Average Health | {{ health_summary.avg_score|default(0)|round(1) }} |
| Grade | {{ health_summary.grade|default("N/A") }} |
| Steps with Gaps | {{ health_summary.steps_with_gaps|default(0) }} |
| Total Gaps | {{ health_summary.total_gaps|default(0) }} |

## Process Flow

{{ mermaid_content }}

## Step-by-Step Journey

| # | Step | Type | Owner | Inputs | Outputs | Systems | Binding | Health | Gaps |
|---|------|------|-------|--------|---------|---------|---------|--------|------|
{% for step in steps -%}
| {{ step.step_number }} | {% if step.capsule_id in critical_path_ids %}**{% endif %}[{{ step.name }}](../{{ step.section }}/{{ step.slug }}/capsule.md){% if step.capsule_id in critical_path_ids %}**{% endif %} | {{ step.task_type }} | {{ step.owner|default("-") }} | {{ step.required_inputs|length }} | {{ step.outputs|length }} | {{ (step.sources + step.sinks)|length }} | {{ step.binding_status }} | {{ step.health_score|round(0)|int }} | {{ step.gaps|length }} |
{% endfor %}

**Bold** steps indicate the critical path.

{% if branch_points %}
## Decision Points

{% for bp in branch_points %}
### {{ bp.gateway_name }}

| Condition | Target |
|-----------|--------|
{% for branch in bp.branches -%}
| {{ branch.condition|default("default") }} | {{ branch.target_name }} |
{% endfor %}

{% endfor %}
{% endif %}
```

**Key template behaviors:**
- Steps on the critical path have their name wrapped in `**bold**` markdown.
- Step names are linked to their capsule page: `../{{ step.section }}/{{ step.slug }}/capsule.md`.
- The `critical_path_ids` variable is a Python set; the `in` operator works in Jinja2.
- Health summary uses `avg_score` (not `avg_health`) with `|default(0)` fallback.
- Decision Points section only renders if `branch_points` is non-empty.

### 5.3 `data-lineage.md.j2` Template

**File:** `templates/mkdocs/data-lineage.md.j2`

**Template variables:**
- `process_name` (str)
- `data_lineage` (list of dicts, each from `DataLineage.to_dict()`)

**Complete template:**

```jinja2
# Data Lineage: {{ process_name }}

## Data Objects

| Data Object | Source | Consumers |
|-------------|--------|-----------|
{% for dl in data_lineage -%}
| **{{ dl.data_name }}** | {{ dl.source_name }} | {{ dl.consumers|map(attribute='name')|join(', ') }} |
{% endfor %}

## Data Flow Details

{% for dl in data_lineage %}
### {{ dl.data_name }}

- **Source**: {{ dl.source_name }}{% if dl.source != "external" %} ([{{ dl.source }}](../tasks/)){% endif %}

- **Consumed by**:
{% for c in dl.consumers %}
  - {{ c.name }} (`{{ c.capsule_id }}`)
{% endfor %}

{% endfor %}
```

**Key template behaviors:**
- Data object names are **bold** in the summary table.
- Consumer names extracted via `|map(attribute='name')|join(', ')`.
- Source links to the tasks directory if not external.
- Each consumer shows name and capsule_id in backticks.

### 5.4 `mkdocs.yml.j2` Nav Addition

In `templates/mkdocs/mkdocs.yml.j2` (lines 45-49):

```yaml
{%- if has_journey %}
  - Journey:
    - Journey Map: journey/index.md
    - Data Lineage: journey/data-lineage.md
{%- endif %}
```

The nav entry appears between "Process Flow" and "Tasks" sections, only when `has_journey` is `True`.

---

## 6. Skill (`.claude/skills/mda-journey/SKILL.md`)

**Complete file:**

```markdown
---
name: mda-journey
description: Show the complete process journey from start to finish. Trace data lineage, see what each step needs and produces, navigate the critical path. Use to understand the full process flow and data dependencies.
argument-hint: [--step <capsule-id>] [--data <data-name>] [--critical-path] [--format yaml|json|mermaid]
allowed-tools: Bash(python *)
---

# MDA Journey -- Process Journey Map & Data Lineage

Shows the complete process journey from start to finish, including what data enters and exits each step, what systems are called, and where decision branches occur.

## Context

Current working directory: !`pwd`
Triples found: !`find . -name "*.cap.md" 2>/dev/null | wc -l || echo "0"`

## Steps

1. Run the journey command:

\```
python cli/mda.py journey $ARGUMENTS
\```

2. Common usage:
   - **Full journey table**: `python cli/mda.py journey`
   - **Single step detail**: `python cli/mda.py journey --step CAP-IV-W2V-001`
   - **Trace a data object**: `python cli/mda.py journey --data borrower_profile`
   - **Show critical path**: `python cli/mda.py journey --critical-path`
   - **Export as YAML**: `python cli/mda.py journey --format yaml`
   - **Mermaid diagram**: `python cli/mda.py journey --format mermaid`

3. For the journey table, explain:
   - Step numbers show the execution order
   - Bold steps are on the critical path (main happy path)
   - Inputs/Outputs columns show data dependency counts
   - Systems column shows external API calls
   - Gaps indicate missing knowledge

4. For data lineage, explain where the data originates and what steps consume it.
```

(Note: The backslash before the triple backticks above is an escaping artifact for this spec only. The actual file uses regular triple backticks.)

---

## 7. Tests (`tests/unit/test_journey_builder.py`)

### 7.0 Test File Setup

```python
"""Tests for the journey builder."""
import importlib.util, os, sys, pytest

_CLI_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "cli")
sys.path.insert(0, _CLI_DIR)
_TESTS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _TESTS_DIR)

# Load journey builder via importlib
_jb_path = os.path.join(_CLI_DIR, "pipeline", "journey_builder.py")
_spec = importlib.util.spec_from_file_location("journey_builder", _jb_path)
jb = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(jb)

from conftest import EXAMPLES_DIR
from config.loader import load_config
```

The test file loads `journey_builder.py` via `importlib.util` rather than a normal import, to work around the module's own `sys.path` manipulation. The loaded module is assigned to the name `jb`.

It imports `EXAMPLES_DIR` from `tests/conftest.py` (which resolves to `{project_root}/examples`) and `load_config` from `cli/config/loader.py`.

### 7.1 Helper: `_make_capsule_data(adj)`

```python
def _make_capsule_data(adj: dict) -> dict:
    """Convert simple adjacency dict {"A": ["B"], "B": []} to capsule_data format."""
    # Build predecessor map from successor map
    predecessors = {k: [] for k in adj}
    for src, succs in adj.items():
        for tgt in succs:
            if tgt in predecessors:
                predecessors[tgt].append(src)

    return {
        k: {"successor_ids": v, "predecessor_ids": predecessors.get(k, [])}
        for k, v in adj.items()
    }
```

Takes a simple adjacency dict like `{"A": ["B"], "B": ["C"], "C": []}` and produces the full `capsule_data` format with both `successor_ids` and `predecessor_ids` for each node.

### 7.2 All 9 Tests

#### Class: `TestTopologicalSort` (4 tests)

**Test 1: `test_linear_chain`**

```python
def test_linear_chain(self):
    data = _make_capsule_data({"A": ["B"], "B": ["C"], "C": []})
    result = jb.topological_sort(data)
    assert result == ["A", "B", "C"]
```

**Test 2: `test_with_branches`**

```python
def test_with_branches(self):
    data = _make_capsule_data({"A": ["B", "C"], "B": ["D"], "C": ["D"], "D": []})
    result = jb.topological_sort(data)
    assert result[0] == "A"
    assert result[-1] == "D"
    assert len(result) == 4
```

**Test 3: `test_single_node`**

```python
def test_single_node(self):
    data = _make_capsule_data({"A": []})
    result = jb.topological_sort(data)
    assert result == ["A"]
```

**Test 4: `test_empty`**

```python
def test_empty(self):
    result = jb.topological_sort({})
    assert result == []
```

#### Class: `TestCriticalPath` (2 tests)

**Test 5: `test_linear`**

```python
def test_linear(self):
    data = _make_capsule_data({"A": ["B"], "B": ["C"], "C": []})
    from models.journey import StepSummary
    steps = [
        StepSummary(step_number=1, capsule_id="A", name="A", task_type="task", owner=None, predecessor_steps=[], successor_steps=["B"]),
        StepSummary(step_number=2, capsule_id="B", name="B", task_type="task", owner=None, predecessor_steps=["A"], successor_steps=["C"]),
        StepSummary(step_number=3, capsule_id="C", name="C", task_type="task", owner=None, predecessor_steps=["B"], successor_steps=[]),
    ]
    result = jb.compute_critical_path(steps, data)
    assert len(result) == 3
    assert result == ["A", "B", "C"]
```

**Test 6: `test_with_branch`**

```python
def test_with_branch(self):
    data = _make_capsule_data({"A": ["B", "C"], "B": ["D"], "C": ["D"], "D": []})
    from models.journey import StepSummary
    steps = [
        StepSummary(step_number=1, capsule_id="A", name="A", task_type="task", owner=None, predecessor_steps=[], successor_steps=["B", "C"]),
        StepSummary(step_number=2, capsule_id="B", name="B", task_type="task", owner=None, predecessor_steps=["A"], successor_steps=["D"]),
        StepSummary(step_number=3, capsule_id="C", name="C", task_type="task", owner=None, predecessor_steps=["A"], successor_steps=["D"]),
        StepSummary(step_number=4, capsule_id="D", name="D", task_type="task", owner=None, predecessor_steps=["B", "C"], successor_steps=[]),
    ]
    result = jb.compute_critical_path(steps, data)
    assert len(result) == 3  # A->B->D or A->C->D
    assert result[0] == "A"
    assert result[-1] == "D"
```

#### Class: `TestBuildJourney` (1 test)

**Test 7: `test_income_verification`**

```python
def test_income_verification(self):
    process_dir = EXAMPLES_DIR / "income-verification"
    config = load_config(process_dir / "mda.config.yaml")
    journey = jb.build_journey(process_dir, config)

    assert journey is not None
    assert journey.total_steps == 8
    assert journey.steps[0].step_number == 1
    assert all(s.capsule_id for s in journey.steps)
    assert "income" in journey.process_name.lower() or "verification" in journey.process_name.lower()
    assert len(journey.critical_path) > 0
    assert "avg_health" in journey.health_summary or "avg_score" in journey.health_summary
```

Assertions:
- Journey is not None.
- Exactly 8 total steps.
- First step has step_number == 1.
- All steps have non-empty capsule_id.
- Process name contains "income" or "verification" (case-insensitive).
- Critical path is non-empty.
- Health summary contains either `avg_health` or `avg_score` key.

#### Class: `TestDataLineage` (1 test)

**Test 8: `test_income_verification_data`**

```python
def test_income_verification_data(self):
    process_dir = EXAMPLES_DIR / "income-verification"
    config = load_config(process_dir / "mda.config.yaml")
    journey = jb.build_journey(process_dir, config)

    assert isinstance(journey.data_lineage, list)
    if journey.data_lineage:
        dl = journey.data_lineage[0]
        assert dl.data_name
        assert dl.source_name
```

Assertions:
- `data_lineage` is a list.
- If non-empty, first entry has truthy `data_name` and `source_name`.

#### Class: `TestBranchPoints` (1 test)

**Test 9: `test_income_verification_branches`**

```python
def test_income_verification_branches(self):
    process_dir = EXAMPLES_DIR / "income-verification"
    config = load_config(process_dir / "mda.config.yaml")
    journey = jb.build_journey(process_dir, config)

    assert isinstance(journey.branch_points, list)
    if journey.branch_points:
        bp = journey.branch_points[0]
        assert bp.gateway_name
        assert len(bp.branches) >= 2
```

Assertions:
- `branch_points` is a list.
- If non-empty, first entry has truthy `gateway_name` and at least 2 branches.

### 7.3 Test Conftest (`tests/conftest.py`)

The tests depend on `tests/conftest.py` which provides:

```python
"""Shared test fixtures for the MDA Intent Layer test suite."""
import sys
import os
from pathlib import Path
import pytest

PROJECT_ROOT = Path(__file__).parent.parent.resolve()
CLI_DIR = PROJECT_ROOT / "cli"
EXAMPLES_DIR = PROJECT_ROOT / "examples"

sys.path.insert(0, str(CLI_DIR))
```

`EXAMPLES_DIR` points to `{project_root}/examples/` which contains the `income-verification` fixture directory.

---

## 8. Verification

Run these commands from the project root to verify the journey system works end-to-end.

### 8.1 Unit Tests

```bash
python -m pytest tests/unit/test_journey_builder.py -v
```

Expected output: 9 tests pass across 5 classes:
- `TestTopologicalSort::test_linear_chain` PASSED
- `TestTopologicalSort::test_with_branches` PASSED
- `TestTopologicalSort::test_single_node` PASSED
- `TestTopologicalSort::test_empty` PASSED
- `TestCriticalPath::test_linear` PASSED
- `TestCriticalPath::test_with_branch` PASSED
- `TestBuildJourney::test_income_verification` PASSED
- `TestDataLineage::test_income_verification_data` PASSED
- `TestBranchPoints::test_income_verification_branches` PASSED

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
- The MkDocs nav includes "Journey" with "Journey Map" and "Data Lineage" sub-items.

---

## 9. Import Pattern

The journey system uses `importlib.util` in three places to avoid circular imports and handle the non-standard package layout where `cli/mda_io/` modules are not importable via normal `import` statements.

### Pattern 1: journey_builder.py loading mda_io modules

```python
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
```

### Pattern 2: docs_generator.py loading journey_builder

```python
import importlib.util as _ilu
_jb_spec = _ilu.spec_from_file_location("journey_builder",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "journey_builder.py"))
_jb_mod = _ilu.module_from_spec(_jb_spec)
_jb_spec.loader.exec_module(_jb_mod)
```

### Pattern 3: test_journey_builder.py loading journey_builder

```python
import importlib.util
_jb_path = os.path.join(_CLI_DIR, "pipeline", "journey_builder.py")
_spec = importlib.util.spec_from_file_location("journey_builder", _jb_path)
jb = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(jb)
```

All three follow the same 4-step pattern:
1. Build file path to the target module.
2. `spec_from_file_location(module_name, file_path)` -- creates a module spec.
3. `module_from_spec(spec)` -- creates an empty module object.
4. `spec.loader.exec_module(mod)` -- executes the module code into the object.

This is required because:
- `cli/mda_io/` uses hyphens-to-underscores naming that breaks normal imports.
- `cli/pipeline/` files are not in a proper package (no `__init__.py` chain from project root).
- The tests directory needs to load modules from `cli/pipeline/` without installing the project.

---

## 10. Dependencies

The journey system requires these Python packages:

| Package | Usage |
|---------|-------|
| `rich` | Console output: `Table`, `Panel`, `box`, `console.print()` with markup |
| `pyyaml` | YAML export (`--format yaml`). Falls back to JSON if not installed. |
| `jinja2` | MkDocs template rendering (via `docs_generator.py`) |

Standard library modules used: `dataclasses`, `typing`, `pathlib`, `collections.deque`, `json`, `warnings`, `importlib.util`, `sys`, `os`.
