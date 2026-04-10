# MDA Intent Layer -- GAP Analysis Report Specification

Recreation specification for the health scoring engine, report generator, and CLI command.
This document contains every weight, deduction, element name, and test assertion needed
to rebuild the feature from scratch.

**Source files:**

| File | Purpose |
|------|---------|
| `cli/models/report.py` | Data models (dataclasses + enum) |
| `cli/pipeline/health_scorer.py` | Scoring engine -- per-triple + process-level |
| `cli/pipeline/report_generator.py` | XML / JSON / YAML output |
| `cli/commands/report_cmd.py` | CLI entry point + Rich console display |
| `.claude/skills/mda-report/SKILL.md` | Skill definition for `/mda-report` |
| `tests/unit/test_health_scorer.py` | 19 tests across 4 test classes |

---

## 1. Overview

The GAP analysis report scores every triple (capsule + intent + contract directory) on
five weighted dimensions, computes a process-level health score, and emits machine-readable
output (XML, JSON, or YAML).

- **Health scoring engine** -- `score_process()` walks every triple directory, calls
  `_score_triple()` for each, checks graph integrity, computes corpus coverage, and
  produces a `ProcessReport`.
- **Report generator** -- `generate_xml()`, `generate_json()`, `generate_yaml()`, and
  `write_report()` serialize the `ProcessReport` into output.
- **CLI command** -- `mda report [--format xml|json|yaml] [--output PATH] ...`
- **Skill** -- `/mda-report` wraps the CLI command.
- **Test suite** -- 19 tests in 4 classes.

---

## 2. Health Score Model

### 2.1 Per-Triple Scoring (5 Dimensions)

Each triple starts at 100 per dimension. Deductions reduce the score. Floor is 0.

| # | Dimension | Weight | Starting Score | Deduction Rules |
|---|-----------|--------|---------------|-----------------|
| 1 | `completeness` | **0.30** | 100 | -20 per missing file (capsule, intent, contract). -10 per missing required field (capsule: `capsule_id`, `bpmn_task_id`, `version`, `status`; intent: `intent_id`, `goal`, `goal_type`; contract: `contract_id`, `binding_status`). -15 per critical gap. Floor 0. |
| 2 | `consistency` | **0.25** | 100 | -25 if `capsule.intent_id != intent.intent_id`. -25 if `capsule.contract_id != contract.contract_id`. -25 if `intent.capsule_id != capsule.capsule_id`. -25 if `intent.contract_ref != contract.contract_id`. -10 if statuses differ across the 3 files. -10 if versions differ across the 3 files. -25 if ID stems differ (strip `CAP-`/`INT-`/`ICT-` prefix). Floor 0. |
| 3 | `schema_compliance` | **0.20** | 100 | -5 per schema validation error (max 3 errors reported per artifact). Runs `validator.validate_capsule()`, `validator.validate_intent()`, `validator.validate_contract()`. Error detail truncated to 80 chars. Floor 0. |
| 4 | `knowledge_coverage` | **0.15** | 100 | -20 if no `corpus_refs` in capsule frontmatter. -20 if capsule body has `<!-- TODO` stubs or body length < 100 chars. -10 per missing body section (`Procedure`, `Business Rules`). -40 if capsule body is entirely empty. +10 bonus if `corpus_refs` has >= 2 entries (capped at 100). Floor 0. |
| 5 | `anti_ui_compliance` | **0.10** | 100 | Set to 0 if `execution_hints.forbidden_actions` is missing any of the 4 required values: `browser_automation`, `screen_scraping`, `ui_click`, `rpa_style_macros`. Set to 0 if `execution_hints` is not a dict or is absent. |

**Weights constant** (defined at module level):

```python
WEIGHTS = {
    "completeness": 0.30,
    "consistency": 0.25,
    "schema_compliance": 0.20,
    "knowledge_coverage": 0.15,
    "anti_ui_compliance": 0.10,
}
```

**Required forbidden actions constant:**

```python
REQUIRED_FORBIDDEN = {"browser_automation", "screen_scraping", "ui_click", "rpa_style_macros"}
```

**ID regex patterns:**

```python
CAP_PAT = re.compile(r"^CAP-[A-Z0-9]{2,3}-[A-Z0-9]{3}-\d{3}$")
INT_PAT = re.compile(r"^INT-[A-Z0-9]{2,3}-[A-Z0-9]{3}-\d{3}$")
ICT_PAT = re.compile(r"^ICT-[A-Z0-9]{2,3}-[A-Z0-9]{3}-\d{3}$")
```

**Triple health score formula:**

```
triple_health = sum(dimension.score * dimension.weight for each dimension)
clamped to [0.0, 100.0]
```

### 2.2 Process Health Score

```
process_score = (triple_avg * 0.70) + (graph_score * 0.15) + (corpus_score * 0.15)
clamped to [0.0, 100.0]
```

Where:

- `triple_avg` = arithmetic mean of all triple health scores
- `graph_score` starts at 100, deductions:
  - -40 if graph is not connected
  - -30 if graph has cycles
  - -15 if zero start events
  - -15 if zero end events
- `corpus_score` = `100.0 * (triples_with_corpus_refs / total_triples)`

### 2.3 Health Grades

| Score Range | Grade | Label |
|------------|-------|-------|
| >= 90 | A | Excellent |
| 80 -- 89 | B | Good |
| 70 -- 79 | C | Acceptable |
| 60 -- 69 | D | Needs Work |
| < 60 | F | Critical |

Implemented by `grade_from_score(score) -> HealthGrade` and `grade_label(grade) -> str`.

---

## 3. Data Models (`cli/models/report.py`)

### 3.1 HealthGrade (Enum)

```python
class HealthGrade(str, Enum):
    A = "A"
    B = "B"
    C = "C"
    D = "D"
    F = "F"
```

### 3.2 grade_from_score(score: float) -> HealthGrade

Returns `A` if score >= 90, `B` if >= 80, `C` if >= 70, `D` if >= 60, else `F`.

### 3.3 grade_label(grade: HealthGrade) -> str

Maps `A` -> `"Excellent"`, `B` -> `"Good"`, `C` -> `"Acceptable"`, `D` -> `"Needs Work"`, `F` -> `"Critical"`.

### 3.4 DimensionScore

```python
@dataclass
class DimensionScore:
    name: str       # completeness, consistency, schema_compliance, knowledge_coverage, anti_ui_compliance
    score: float    # 0-100
    weight: float   # 0.0-1.0
    details: list[str] = field(default_factory=list)  # what was deducted and why
```

### 3.5 GapEntry

```python
@dataclass
class GapEntry:
    gap_type: str       # e.g. "missing_field", "ambiguous_rule"
    severity: str       # critical, high, medium, low
    description: str
    triple_id: str
    source: str         # "capsule_frontmatter" or "gap_file"
```

### 3.6 TripleFileInfo

```python
@dataclass
class TripleFileInfo:
    artifact_type: str          # capsule, intent, contract
    artifact_id: str            # e.g. "CAP-IV-RCV-001"
    status: str                 # e.g. "draft", "review", "approved"
    binding_status: Optional[str] = None  # only for contracts
```

### 3.7 TripleScore

```python
@dataclass
class TripleScore:
    triple_id: str
    triple_name: str
    bpmn_task_type: str
    health_score: float
    grade: HealthGrade
    dimensions: list[DimensionScore] = field(default_factory=list)
    gaps: list[GapEntry] = field(default_factory=list)
    files: list[TripleFileInfo] = field(default_factory=list)
```

Has `to_dict()` method that returns:

```python
{
    "triple_id": str,
    "name": str,           # from triple_name
    "type": str,           # from bpmn_task_type
    "health_score": float, # rounded to 1 decimal
    "grade": str,          # enum value
    "dimensions": [{"name": str, "score": float, "weight": float, "details": list[str]}],
    "gaps": [{"type": str, "severity": str, "description": str}],
    "files": [{"type": str, "id": str, "status": str, "binding": Optional[str]}],
}
```

### 3.8 GapSummary

```python
@dataclass
class GapSummary:
    total: int = 0
    critical: int = 0
    high: int = 0
    medium: int = 0
    low: int = 0
```

Has `to_dict()` returning all 5 fields.

### 3.9 CorpusCoverage

```python
@dataclass
class CorpusCoverage:
    matched_docs: int = 0
    total_corpus_docs: int = 0
    triples_with_corpus_refs: int = 0
```

Has `to_dict()` returning all 3 fields.

### 3.10 GraphIntegrity

```python
@dataclass
class GraphIntegrity:
    connected: bool = True
    cycles: bool = False
    start_events: int = 0
    end_events: int = 0
```

Has `to_dict()` returning all 4 fields.

### 3.11 ProcessReport

```python
@dataclass
class ProcessReport:
    process_id: str
    process_name: str
    generated: str                 # ISO timestamp with trailing "Z"
    health_score: float
    grade: HealthGrade
    grade_label: str
    gap_summary: GapSummary = field(default_factory=GapSummary)
    schema_violations: int = 0
    cross_ref_errors: int = 0
    triple_scores: list[TripleScore] = field(default_factory=list)
    corpus_coverage: CorpusCoverage = field(default_factory=CorpusCoverage)
    graph_integrity: GraphIntegrity = field(default_factory=GraphIntegrity)
```

Has `to_dict()` method. Adds computed field `"total_triples": len(self.triple_scores)`.
`health_score` is rounded to 1 decimal in the dict.

---

## 4. Scoring Engine (`cli/pipeline/health_scorer.py`)

### 4.1 Module-Level Setup

Dynamically loads three IO modules via `importlib.util`:
- `cli/mda_io/frontmatter.py` -- for `read_frontmatter_file()`
- `cli/mda_io/yaml_io.py` -- for YAML operations
- `cli/mda_io/schema_validator.py` -- for `SchemaValidator`

Imports all report models from `cli/models/report.py`.

### 4.2 score_process()

```python
def score_process(
    project_root: Path,
    config,
    schemas_dir: Optional[Path] = None,
    corpus_dir: Optional[Path] = None
) -> ProcessReport:
```

**Algorithm:**

1. Resolve `triples_dir` from `config.get("paths.triples")` or `config.get("output.triples_dir")` or default `"triples"`.
2. Resolve `decisions_dir` from `config.get("paths.decisions")` or `config.get("output.decisions_dir")` or default `"decisions"`.
3. Get `process_id` from `config.get("process.id", "unknown")`.
4. Get `process_name` from `config.get("process.name", ...)` with fallback to directory name title-cased.
5. Create `SchemaValidator(schemas_dir)` if schemas_dir exists.
6. Discover triple directories via `_discover_triple_dirs()`.
7. For each triple dir, call `_score_triple()`. Accumulate gaps, schema violations, xref errors, capsule data, corpus ref counts.
8. Build `GapSummary` by counting severities.
9. Build `CorpusCoverage` -- count `*.corpus.md` files in corpus_dir recursively.
10. Call `_check_graph_integrity()` with collected capsule frontmatter data.
11. Compute process score (see formula in section 2.2).
12. Return `ProcessReport` with `generated = datetime.utcnow().isoformat() + "Z"`.

### 4.3 _discover_triple_dirs()

```python
def _discover_triple_dirs(triples_dir, decisions_dir) -> list[Path]:
```

Iterates both `triples_dir` and `decisions_dir`. For each, collects sorted subdirectories
that are directories and do not start with `_`. Returns flat list.

### 4.4 _score_triple()

```python
def _score_triple(triple_dir: Path, validator) -> TripleScore:
```

1. Glob for `*.cap.md`, `*.intent.md`, `*.contract.md`.
2. Read frontmatter from each file using `frontmatter_mod.read_frontmatter_file()`.
3. Extract `triple_id` (capsule_id with `CAP-` stripped, fallback to dir name), `triple_name` (from `bpmn_task_name`), `task_type` (from `bpmn_task_type`).
4. Collect gaps from `capsule_fm.gaps[]` as `GapEntry` objects with `source="capsule_frontmatter"`.
5. Build `TripleFileInfo` list from each present file's frontmatter.
6. Score all 5 dimensions (see section 2.1 for exact deduction rules).
7. Compute weighted health score.
8. Return `TripleScore` with grade from `grade_from_score()`.

### 4.5 _check_graph_integrity()

```python
def _check_graph_integrity(capsule_data: dict) -> GraphIntegrity:
```

Input: `capsule_data` is `{capsule_id: frontmatter_dict}`.

**Empty input:** Returns `GraphIntegrity(connected=False, cycles=False, start_events=0, end_events=0)`.

**Start/end detection:**
- Start event = capsule with no `predecessor_ids` (empty or missing).
- End event = capsule with no `successor_ids` (empty or missing).

**Connectivity check (BFS):**
1. Build undirected adjacency list from `successor_ids` and `predecessor_ids`.
2. Pick start node: first capsule with no predecessors, else first capsule in dict.
3. BFS from start node, only visiting nodes in `all_ids` (known capsules).
4. Connected if `visited == all_ids` or `len(all_ids) <= 1`.

**Cycle detection (iterative DFS):**
1. Maintain `dfs_visited` and `in_stack` sets.
2. For each unvisited node, push onto stack as `(node, False)`.
3. On pop: if `processed=True`, remove from `in_stack`. If `node in in_stack`, cycle found. If unvisited, add to both sets, push `(node, True)` sentinel, then push successors.
4. Before pushing a successor, check if it is already `in_stack` -- if so, cycle found.
5. Only follows `successor_ids` (directed edges) for cycle detection.

---

## 5. Report Generator (`cli/pipeline/report_generator.py`)

### 5.1 XML Format -- `generate_xml(report) -> str`

Produces pretty-printed XML with declaration `<?xml version="1.0" encoding="UTF-8"?>`.

**Complete element structure:**

```xml
<?xml version="1.0" encoding="UTF-8"?>
<mda-report version="1.0" generated="{ISO_TIMESTAMP}">
  <process id="{process_id}" name="{process_name}">

    <health-score value="{score}" grade="{A-F}" label="{Excellent|Good|...}"/>

    <summary>
      <total-triples>{N}</total-triples>
      <gaps total="{N}" critical="{N}" high="{N}" medium="{N}" low="{N}"/>
      <schema-violations>{N}</schema-violations>
      <cross-ref-errors>{N}</cross-ref-errors>
    </summary>

    <triples>
      <triple id="{triple_id}" name="{triple_name}" type="{bpmn_task_type}">
        <health-score value="{score}" grade="{A-F}"/>
        <dimensions>
          <completeness score="{score}">
            <detail>{text}</detail>
          </completeness>
          <consistency score="{score}">
            <detail>{text}</detail>
          </consistency>
          <schema-compliance score="{score}">
            <detail>{text}</detail>
          </schema-compliance>
          <knowledge-coverage score="{score}">
            <detail>{text}</detail>
          </knowledge-coverage>
          <anti-ui-compliance score="{score}">
            <detail>{text}</detail>
          </anti-ui-compliance>
        </dimensions>
        <gaps>
          <gap type="{gap_type}" severity="{severity}">{description}</gap>
        </gaps>
        <files>
          <capsule id="{id}" status="{status}"/>
          <intent id="{id}" status="{status}"/>
          <contract id="{id}" status="{status}" binding="{binding_status}"/>
        </files>
      </triple>
    </triples>

    <corpus-coverage>
      <matched-docs>{N}</matched-docs>
      <total-corpus-docs>{N}</total-corpus-docs>
      <triples-with-corpus-refs>{N}</triples-with-corpus-refs>
    </corpus-coverage>

    <graph-integrity>
      <connected>{true|false}</connected>
      <cycles>{true|false}</cycles>
      <start-events>{N}</start-events>
      <end-events>{N}</end-events>
    </graph-integrity>

  </process>
</mda-report>
```

**Implementation notes:**
- Dimension element names use hyphens (Python `name.replace("_", "-")`).
- Only first 3 detail entries are emitted per dimension (`d.details[:3]`).
- Contract file element includes `binding` attribute only if `binding_status` is truthy.
- Boolean values in `<graph-integrity>` are lowercase strings (`str(...).lower()`).
- Pretty-printing uses `xml.dom.minidom.parseString().toprettyxml(indent="  ")`.
- The minidom XML declaration line is replaced to ensure `encoding="UTF-8"`.

### 5.2 JSON Format -- `generate_json(report, indent=2) -> str`

```python
json.dumps(report.to_dict(), indent=indent, default=str)
```

Uses the `ProcessReport.to_dict()` serialization (see section 3.11).

### 5.3 YAML Format -- `generate_yaml(report) -> str`

```python
yaml_io.dump_yaml_string(report.to_dict())
```

Uses the same dict structure as JSON.

### 5.4 write_report()

```python
def write_report(report: ProcessReport, output_path: Path, fmt: str = "xml") -> None:
```

1. Creates parent directories (`output_path.parent.mkdir(parents=True, exist_ok=True)`).
2. Calls the appropriate `generate_*()` function based on `fmt`.
3. Writes content with `encoding="utf-8"`.
4. Raises `ValueError` for unknown format.

---

## 6. CLI Command

### 6.1 Argparse Registration (in `cli/mda.py`)

```python
report_parser = subparsers.add_parser("report", help="Generate GAP analysis report with health scoring")
report_parser.add_argument("--format", choices=["xml", "json", "yaml"], default="xml",
                           help="Output format")
report_parser.add_argument("--output", type=Path,
                           help="Write report to file")
report_parser.add_argument("--severity-threshold", choices=["critical", "high", "medium", "low"],
                           default="low", help="Minimum severity to include")
report_parser.add_argument("--include-details", action="store_true",
                           help="Include detailed dimension breakdowns")
report_parser.add_argument("--no-score", action="store_true",
                           help="Skip scoring, just list gaps")
```

### 6.2 Dispatch (in `cli/mda.py`)

```python
elif args.command == "report":
    from commands.report_cmd import run_report
    run_report(args, config)
```

### 6.3 run_report() (in `cli/commands/report_cmd.py`)

```python
def run_report(args, config):
```

1. Gets `project_root`, `schemas_dir`, `corpus_dir` from config.
2. Calls `score_process(project_root, config, schemas_dir, corpus_dir)`.
3. Reads `fmt` from `args.format` (default `"xml"`), `output_path` from `args.output`.
4. If `output_path` is set: calls `write_report()` and prints success message.
5. If no output path: calls `_print_console_report(report)` then prints in requested format to stdout.

### 6.4 _print_console_report()

Uses Rich library to display:
- Process name, health score with grade coloring, gap summary, graph status.
- A `Table` with columns: Triple, Type, Score, Grade, Gaps, Comp, Cons, Schema, Know, AntiUI.
- Grade colors: `A`=green, `B`=blue, `C`=yellow, `D`=red, `F`=bold red.
- Triple names truncated to 30 chars.
- Table style: `box.SIMPLE_HEAVY`.

---

## 7. Skill (`.claude/skills/mda-report/SKILL.md`)

**Frontmatter:**

```yaml
---
name: mda-report
description: >-
  Generate a GAP analysis report with health scoring for the current process.
  Scores each triple on 5 dimensions (completeness, consistency, schema compliance,
  knowledge coverage, anti-UI compliance) and produces XML/JSON/YAML output.
  Use to assess process health before review.
argument-hint: "[--format xml|json|yaml] [--output path]"
allowed-tools: Bash(python *)
---
```

**Body content:**

1. Title: "MDA Report -- GAP Analysis & Health Scoring"
2. Context section with dynamic checks: `pwd`, config exists, triple count (glob `*.cap.md`), gap count (grep `severity:` in triples/ and decisions/).
3. Steps:
   - Run `python cli/mda.py report $ARGUMENTS`
   - Available options: `--format`, `--output`, `--include-details`
   - Dimension breakdown with weights
   - Grade scale
   - Post-report: suggest improvements for D/F triples

---

## 8. Tests (`tests/unit/test_health_scorer.py`)

19 tests across 4 classes. All tests use the `income-verification` example process
under `EXAMPLES_DIR`.

### 8.1 TestGradeFromScore (7 tests)

| Test | Assertion |
|------|-----------|
| `test_grade_a` | `grade_from_score(95) == HealthGrade.A` |
| `test_grade_b` | `grade_from_score(85) == HealthGrade.B` |
| `test_grade_c` | `grade_from_score(75) == HealthGrade.C` |
| `test_grade_d` | `grade_from_score(65) == HealthGrade.D` |
| `test_grade_f` | `grade_from_score(50) == HealthGrade.F` |
| `test_grade_boundary_90` | `grade_from_score(90) == HealthGrade.A` |
| `test_grade_boundary_0` | `grade_from_score(0) == HealthGrade.F` |

### 8.2 TestGradeLabel (1 test)

| Test | Assertion |
|------|-----------|
| `test_labels` | Verifies all 5 mappings: A=Excellent, B=Good, C=Acceptable, D=Needs Work, F=Critical |

### 8.3 TestScoreProcess (6 tests)

All load config from `EXAMPLES_DIR / "income-verification" / "mda.config.yaml"` and
call `scorer.score_process()`.

| Test | Assertion |
|------|-----------|
| `test_income_verification_scores` | Report is `ProcessReport`, score in [0, 100], grade is valid `HealthGrade`, 8 triple scores (6 triples + 2 decisions), `process_id == "Process_IncomeVerification"` |
| `test_all_triples_scored` | Every triple has score in [0, 100], exactly 5 dimensions, valid grade |
| `test_dimension_weights_sum_to_1` | For each triple, `sum(d.weight) == 1.0` (within 0.01 tolerance) |
| `test_gap_summary_populated` | `total == critical + high + medium + low` |
| `test_graph_integrity` | `cycles == False`, `start_events >= 1` |
| `test_to_dict_round_trips` | Dict has keys `health_score`, `grade`, `triple_scores`; `triple_scores` length == 8 |

### 8.4 TestReportGenerator (5 tests)

| Test | Assertion |
|------|-----------|
| `test_xml_output` | XML starts with `<?xml`, contains `<mda-report`, `<health-score`, `<triple` |
| `test_json_output` | Parses as valid JSON, has keys `health_score` and `triple_scores` |
| `test_yaml_output` | Parses as valid YAML, has key `health_score` |
| `test_write_xml_file` | File exists at `tmp_path / "report.xml"`, content contains `<mda-report` |
| `test_all_three_processes` | Runs all 3 demo processes (`loan-origination`, `income-verification`, `property-appraisal`), each produces score in [0, 100] and at least 1 triple |

### 8.5 Test Infrastructure

Tests use dynamic module loading (`importlib.util`) to load `health_scorer.py` and
`report_generator.py` directly. They import `PROJECT_ROOT`, `EXAMPLES_DIR`,
`SCHEMAS_DIR`, `CORPUS_DIR` from `tests/conftest.py` and `load_config` from
`cli/config/loader.py`.

---

## 9. Verification

### 9.1 Run the Tests

```bash
python -m pytest tests/unit/test_health_scorer.py -v
```

Expected: 19 tests pass (7 + 1 + 6 + 5).

### 9.2 Run the CLI Command

```bash
# XML to stdout (default)
python cli/mda.py report

# JSON to file
python cli/mda.py report --format json --output report.json

# YAML to stdout
python cli/mda.py report --format yaml
```

### 9.3 Verify Output Structure

- XML: must start with `<?xml version="1.0" encoding="UTF-8"?>`, root is `<mda-report>`.
- JSON: must parse as valid JSON, top-level keys include `process_id`, `health_score`, `grade`, `triple_scores`.
- YAML: must parse as valid YAML, same key structure as JSON.

### 9.4 Verify Scoring

- Every triple has exactly 5 dimensions with weights summing to 1.0.
- Process score is in [0, 100].
- Grade matches score range (A >= 90, B >= 80, ...).
- Gap summary counts match individual gap severities.
- Graph integrity reflects actual process graph connectivity.

### 9.5 Verify Against Demo Data

The `examples/` directory contains 3 demo processes. All three must produce valid reports:
- `examples/income-verification/` -- 8 scored items (6 triples + 2 decisions)
- `examples/loan-origination/`
- `examples/property-appraisal/`
