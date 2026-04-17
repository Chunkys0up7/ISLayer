# Triple Flow Simulator — Phase 1 Recreation Specification

> **Purpose of this document.** Everything an engineer needs to rebuild Phase 1 of the Triple Flow Simulator from scratch, with no access to the source repository. Every file, every public function signature, every invariant check, every SQL column, every grammar rule, and every test fixture is captured here.

---

## 1. Executive Summary

**System.** The Triple Flow Simulator is a diagnostic harness for inter-triple handoffs in MDA (Model-Driven Architecture) Intent Layer processes. Given a corpus of CIM→PIM→PSM triples (one per BPMN step or decision), it produces a ranked defect backlog rather than a pass/fail verdict.

**Phase 1 scope — Foundation.** Ingest triples, run a fixed set of structural invariant checks against them, produce a classified finding set and an inventory report. **Zero LLM calls** in Phase 1. This is the first value delivery: the engineer can already triage a real corpus before any simulation logic is built.

**Size.**

- 27 Python files (plus `schema.sql`, `grammar.lark`, `rules.yaml`, one default config YAML).
- ~2,500 lines of source code (total including tests: ~4,500 LOC).
- 86 passing tests (unit + integration).

**Runtime dependencies (pyproject.toml).**

- `pyyaml>=6.0`
- `pydantic>=2.0`
- `networkx>=3.0`
- `click>=8.0`
- `lark>=1.1`
- `gitpython>=3.1`
- `jinja2>=3.1`

**Dev dependencies:** `pytest>=8.0`, `pytest-cov>=4.0`.

**Python:** `>=3.10` (tested on 3.10, 3.11, 3.12, 3.13).

**Outputs per run.** A run directory `reports/<run_id>/` containing:

- `findings.db` — SQLite findings store (see §4.5 schema).
- `inventory.md` — human-readable markdown report.
- `inventory.json` — machine-readable JSON report.

**Run ID format.** `YYYYMMDDTHHMMSS-<8-hex>` (e.g., `20260415T142301-ab12cd34`).

---

## 2. Package Layout

Complete directory tree with source LOC per file. All source is under `triple_flow_sim/`.

```
triple-flow-sim/
  pyproject.toml                                          58 lines
  README.md                                               57 lines
  config/
    loader.default.yaml                                   42 lines
  triple_flow_sim/
    __init__.py                                            8    # __version__ and TAXONOMY_VERSION
    cli.py                                               193    # click entry point (inventory, load)
    config.py                                             82    # YAML config loader with deep merge
    logging_setup.py                                      22    # stderr logger
    contracts/
      __init__.py                                         46    # re-exports
      triple.py                                          235    # Triple, TripleSet, LoadReport
      finding.py                                         172    # Finding, RawDetection, taxonomy enums
      journey_context.py                                 125    # JourneyContext (Phase 3 populates)
      trace.py                                           191    # Trace (Phase 2/3 populate)
    evaluator/
      __init__.py                                         30    # ExpressionEvaluator facade
      grammar.lark                                        63    # (see §4.6)
      parser.py                                          199    # lark -> AST
      ast_nodes.py                                        77    # pydantic AST node models
    components/
      c01_loader/
        __init__.py                                        2
        loader.py                                        217    # TripleLoader facade
        adapter_mda.py                                   495    # MDA format (cap/intent/contract)
        adapter_native.py                                 ~80   # native YAML/JSON
        normalizer.py                                     ~70   # identity + defaulting
        source_local.py                                   22    # resolve local path
        source_git.py                                     82    # clone_or_update
      c02_inventory/
        __init__.py                                       11
        inventory.py                                     117    # TripleInventory facade
        completeness_matrix.py                            70    # build_matrix, render_markdown
        naming_drift.py                                   96    # detect_naming_drift
        invariants/
          __init__.py                                     31    # INVARIANTS = (i01_identity, ...)
          i01_identity.py                                 39
          i02_layer.py                                    31
          i03_intent.py                                   48
          i04_contract.py                                 47
          i05_gateway_predicates.py                       41
          i06_obligation_closure.py                       56
          i07_state_flow.py                               98
          i08_content_presence.py                         45
          i09_predicate_evaluability.py                   63
          i10_regulatory_resolution.py                    51
      c03_graph/
        __init__.py                                       23
        graph.py                                         262    # JourneyGraph
        bpmn_parser.py                                   243    # parse_bpmn -> BpmnGraphData
        binder.py                                         89    # bind triples to BPMN nodes
        critical_path.py                                  75    # compute_critical_path
      c11_classifier/
        __init__.py                                        7
        classifier.py                                    165    # FindingClassifier
        templates.py                                      29    # Jinja2 render()
        rules.yaml                                       156
      c12_store/
        __init__.py                                        7
        store.py                                         338    # FindingStore
        schema.sql                                        59
    reports/
      __init__.py                                         0
      inventory_report.py                                140
  tests/
    fixtures/
      bpmn/                                             (BPMN XML fixtures)
      corpus_clean/                                     (well-formed MDA triples)
      corpus_seeded/                                    (seeded defects)
    unit/
      c01/                                              (loader tests)
      c02/                                              (10 invariants + inventory tests)
      c03/                                              (graph / binder tests)
      c11/                                              (classifier tests)
      c12/                                              (store tests)
      evaluator/                                        (grammar parse tests)
    integration/                                        (end-to-end CLI tests)
```

---

## 3. Contracts (Pydantic Models)

All models use `ConfigDict(extra="allow")` so unmapped fields are preserved silently. Fields with `None` defaults are semantically distinct from empty lists and this distinction is load-bearing for invariants I4 and I7.

### 3.1 `contracts/triple.py` — Triple and supporting types

**Enums.**

```python
class BpmnNodeType(str, Enum):
    TASK = "task"
    EXCLUSIVE_GATEWAY = "exclusive_gateway"
    PARALLEL_GATEWAY = "parallel_gateway"
    START_EVENT = "start_event"
    END_EVENT = "end_event"
    INTERMEDIATE_EVENT = "intermediate_event"

class ContentType(str, Enum):
    KNOWLEDGE = "knowledge"
    REGULATORY = "regulatory"
    JOB_AID = "job_aid"

class ObligationType(str, Enum):
    OPENS = "opens"
    CLOSES = "closes"
    ENFORCES = "enforces"
    REFERENCES = "references"

class AssertionPredicate(str, Enum):
    EXISTS = "exists"
    EQUALS = "equals"
    IN_RANGE = "in_range"
    MATCHES_PATTERN = "matches_pattern"
    SATISFIES_EXPRESSION = "satisfies_expression"
```

**Subtypes.**

```python
class StateFieldRef(BaseModel):
    path: str
    type: str = "any"
    namespace: Optional[str] = None

class ContextAssertion(BaseModel):
    path: str
    predicate: AssertionPredicate = AssertionPredicate.EXISTS
    value: Any = None
    type: str = "any"
    source_triple: Optional[str] = None

class MustCloseBy(BaseModel):
    condition: str
    anchor: Optional[StateFieldRef] = None

class ObligationSpec(BaseModel):
    obligation_id: str
    description: str = ""
    regulatory_ref: Optional[str] = None
    must_close_by: Optional[MustCloseBy] = None
    close_conditions: list[ContextAssertion] = []
    exits_journey: bool = False

class BranchPredicate(BaseModel):
    edge_id: str
    predicate_expression: str
    evidence_refs: list[str] = []
    is_default: bool = False

class RetrievalMetadata(BaseModel):
    retrieved_at: Optional[str] = None
    retrieval_confidence: Optional[float] = None
    source_span: Optional[dict] = None

class ContentChunk(BaseModel):
    chunk_id: str
    source_document: str = ""
    content_type: ContentType = ContentType.KNOWLEDGE
    text: str = ""
    retrieval_metadata: Optional[RetrievalMetadata] = None

class ToolRef(BaseModel):
    tool_id: str
    purpose: str = ""
    mock_response_template: Optional[str] = None

class RegulatoryRef(BaseModel):
    citation: str
    rule_text: str = ""
    obligation_type: ObligationType = ObligationType.REFERENCES

class BusinessRule(BaseModel):
    rule_id: str
    rule_text: str = ""
    evaluable_form: Optional[str] = None
```

**Layer objects.**

```python
class CIMLayer(BaseModel):
    intent: str = ""
    regulatory_refs: list[RegulatoryRef] = []
    business_rules: list[BusinessRule] = []

class PIMLayer(BaseModel):
    # NOTE: None = "not declared" vs [] = "explicitly empty".
    # Invariants I4 and I7 depend on this distinction.
    preconditions: Optional[list[ContextAssertion]] = None
    postconditions: Optional[list[ContextAssertion]] = None
    obligations_opened: Optional[list[ObligationSpec]] = None
    obligations_closed: Optional[list[str]] = None
    decision_predicates: Optional[list[BranchPredicate]] = None
    state_writes: Optional[list[StateFieldRef]] = None
    state_reads: Optional[list[StateFieldRef]] = None

class PSMLayer(BaseModel):
    enriched_content: list[ContentChunk] = []
    prompt_scaffold: Optional[str] = None
    tool_bindings: list[ToolRef] = []
```

**Top-level.**

```python
class Triple(BaseModel):
    triple_id: str
    version: str = "0"
    bpmn_node_id: str = ""
    bpmn_node_type: BpmnNodeType = BpmnNodeType.TASK
    cim: Optional[CIMLayer] = None
    pim: Optional[PIMLayer] = None
    psm: Optional[PSMLayer] = None
    source_path: Optional[str] = None
    raw: Optional[dict] = None

class TripleSet(BaseModel):
    triples: dict[str, Triple] = {}
    corpus_version_hash: str = ""
    # Implements __iter__, __len__, __contains__, get()

class LoadReport(BaseModel):
    total_files_attempted: int = 0
    successful_loads: int = 0
    failed_loads: list[dict] = []           # [{path, error_message}]
    identity_failures: list[dict] = []      # [{path, missing_fields}]
    field_mapping_applied: dict = {}
    raw_preservation: list[str] = []
    corpus_version_hash: str = ""
    source_format: str = ""
    source_path: str = ""
```

### 3.2 `contracts/finding.py` — Finding and taxonomy

**Taxonomy enums.**

```python
class Layer(str, Enum):
    CIM = "CIM"; PIM = "PIM"; PSM = "PSM"; NA = "N/A"

class Generator(str, Enum):
    INVENTORY = "inventory"
    STATIC_HANDOFF = "static_handoff"
    GROUNDED_PAIR = "grounded_pair"
    SEQUENCE_RUN = "sequence_run"
    CONTEXT_ISOLATION = "context_isolation"
    BRANCH_BOUNDARY = "branch_boundary"
    PERTURBATION = "perturbation"
    ABLATION = "ablation"
    VOLUME = "volume"

class Severity(str, Enum):
    REGULATORY = "regulatory"
    CORRECTNESS = "correctness"
    EFFICIENCY = "efficiency"
    COSMETIC = "cosmetic"

class Confidence(str, Enum):
    HIGH = "high"; MEDIUM = "medium"; LOW = "low"

class FindingStatus(str, Enum):
    NEW = "new"; TRIAGED = "triaged"; ACCEPTED = "accepted"
    SUPPRESSED = "suppressed"; FIXED = "fixed"; REGRESSED = "regressed"

class DefectClass(str, Enum):
    # Structure
    LAYER_MISSING = "layer_missing"
    IDENTITY_INCOMPLETE = "identity_incomplete"
    ORPHAN_TRIPLE = "orphan_triple"
    ORPHAN_OBLIGATION = "orphan_obligation"
    REGULATORY_ORPHAN = "regulatory_orphan"
    # Contract
    CONTRACT_MISSING = "contract_missing"
    OUTPUT_UNDER_DECLARATION = "output_under_declaration"
    OUTPUT_OVER_PROMISE = "output_over_promise"
    INPUT_UNDER_DECLARATION = "input_under_declaration"
    TYPE_MISMATCH = "type_mismatch"
    STATE_FLOW_GAP = "state_flow_gap"
    SILENT_OVERWRITE = "silent_overwrite"
    # Decision
    EVALUABILITY_GAP = "evaluability_gap"
    PREDICATE_NON_PARTITIONING = "predicate_non_partitioning"
    BRANCH_MISDIRECTION = "branch_misdirection"
    ESCALATION_FAILURE = "escalation_failure"
    # Content
    CONTENT_MISSING = "content_missing"
    CONTENT_STALE = "content_stale"
    CONTENT_ADJACENT_NOT_ACTIONABLE = "content_adjacent_not_actionable"
    CONTENT_CONTRADICTS = "content_contradicts"
    # Handoff
    HANDOFF_CARRIED_BY_EXTERNAL_CONTEXT = "handoff_carried_by_external_context"
    HANDOFF_FORMAT_MISMATCH = "handoff_format_mismatch"
    HANDOFF_IMPLICIT_SETUP = "handoff_implicit_setup"
    HANDOFF_NAMING_DRIFT = "handoff_naming_drift"
    # Journey
    CUMULATIVE_DRIFT = "cumulative_drift"
    CONTEXT_BLOAT = "context_bloat"
    JOURNEY_STUCK = "journey_stuck"
    REGULATORY_VIOLATION = "regulatory_violation"
```

**Records.**

```python
class Evidence(BaseModel):
    journey_id: Optional[str] = None
    step_index: Optional[int] = None
    observed: Any = None
    expected: Any = None
    trace_ref: str = ""

class RawDetection(BaseModel):
    signal_type: str                              # key into rules.yaml
    generator: Generator
    primary_triple_id: Optional[str] = None
    related_triple_ids: list[str] = []
    bpmn_node_id: Optional[str] = None
    bpmn_edge_id: Optional[str] = None
    detector_context: dict = {}
    evidence: Optional[Evidence] = None

class Finding(BaseModel):
    finding_id: str = uuid4_str
    detected_at: datetime = utcnow
    taxonomy_version: str = "1.0.0"
    layer: Layer
    defect_class: DefectClass
    generator: Generator
    severity: Severity = Severity.CORRECTNESS
    confidence: Confidence = Confidence.HIGH
    primary_triple_id: str = ""
    related_triple_ids: list[str] = []
    bpmn_node_id: str = ""
    bpmn_edge_id: Optional[str] = None
    summary: str = ""
    detail: str = ""
    evidence: Evidence = Evidence()
    journeys_affected_count: int = 0
    journeys_affected_pct: float = 0.0
    is_on_critical_path: bool = False
    status: FindingStatus = FindingStatus.NEW
    suppression_reason: Optional[str] = None
    first_seen_run: str = ""
    last_seen_run: str = ""
    occurrence_count: int = 1
```

### 3.3 `contracts/journey_context.py` — Phase 1 stub, Phase 3 populates

Build all models now for forward compatibility. Mutation discipline (M1-M5) is not enforced in Phase 1. Classes (all `BaseModel` with `extra="allow"`):

- `ExecutionMode(str, Enum)` — `STATIC`, `GROUNDED`, `ISOLATED`
- `ProvenanceEntry` — `written_by_triple`, `written_at_step`, `value_hash`, `derived_from`
- `ProvenanceLog` — `entries: dict[str, list[ProvenanceEntry]]`
- `LLMInteractionRecord` — `model`, `model_version`, `temperature`, `seed`, `prompt_template_version`, `prompt_sent`, `content_provided`, `context_provided`, `raw_response`, `parsed_response`, `token_counts`, `refusals`
- `NodeExecution` — full runtime state per step
- `OpenObligation`, `ClosedObligation`, `Attestation`
- `JourneyContext` — `journey_id`, `persona_id`, `started_at`, `current_node`, `corpus_version`, `journey_spec_version`, `state`, `provenance`, `history`, `open_obligations`, `closed_obligations`, `attestations`

### 3.4 `contracts/trace.py` — Phase 1 stub

Classes: `TraceMode`, `TraceOutcome`, `IsolationOutcome` (enums); `StateDiff`, `StaticResult`, `DivergenceSignature`, `IsolationResult`, `BranchEvaluationRecord`, `TraceStep`, `GeneratorConfig`, `LLMConfig`, `TraceMetrics`, `Persona`, `Trace`.

Phase 1 only uses `TraceMode.INVENTORY` and `TraceOutcome.REPORT_ONLY` in the `inventory` CLI path.

### 3.5 `contracts/__init__.py`

Re-exports the public surface so callers can `from triple_flow_sim.contracts import ...`:

```python
from .triple import (
    AssertionPredicate, BpmnNodeType, BranchPredicate, BusinessRule,
    CIMLayer, ContentChunk, ContentType, ContextAssertion, LoadReport,
    MustCloseBy, ObligationSpec, ObligationType, PIMLayer, PSMLayer,
    RegulatoryRef, RetrievalMetadata, StateFieldRef, ToolRef, Triple, TripleSet,
)
from .finding import (
    Confidence, DefectClass, Evidence, Finding, FindingStatus,
    Generator, Layer, RawDetection, Severity,
)
from .journey_context import JourneyContext, LLMInteractionRecord, NodeExecution
from .trace import Trace, TraceMode, TraceOutcome, TraceStep
```

---

## 4. Components

### 4.1 Component 01 — Triple Loader

**Purpose.** Ingest a corpus of triples from either an MDA-format directory tree or native YAML/JSON files, normalize them against the target `Triple` schema, produce a `TripleSet` keyed by `triple_id` plus a `LoadReport`.

**Dual-adapter architecture.**

- `adapter_mda` — MDA project format (one directory per triple: `*.cap.md`, `*.intent.md`, `*.contract.md`, optional `*.jobaid.yaml`).
- `adapter_native` — one YAML or JSON file per triple, conforming verbatim to the `Triple` schema.
- A `TripleLoader` facade dispatches to the right adapter based on `source_format` config.

**Loader pipeline (B1-B8 behavior blocks).**

- **B1 Resolve source.** `source.type=local` → resolve path against project root. `source.type=git` → clone/pull into `cache/repos/<hash>` using gitpython, then optionally descend to `source.subdir`.
- **B2 Discover.** For MDA: walk `{root}/triples/` and `{root}/decisions/` looking for subdirectories containing a `*.cap.md`; fallback is `rglob("*.cap.md")` if conventional layout is absent. For native: glob `*.yaml`/`*.yml`/`*.json` under the root.
- **B3 Parse.** Each candidate is passed to its adapter; malformed inputs produce an entry on `LoadReport.failed_loads` without aborting the pipeline.
- **B4 Field mapping.** Reserved; `field_mapping` config is copied into `LoadReport.field_mapping_applied` but no-op in Phase 1.
- **B5 Validate identity.** `normalizer.validate_identity(triple)` returns a list of missing fields; any triple missing identity goes to `LoadReport.identity_failures` and is dropped.
- **B6 Normalize.** `normalizer.normalize(triple)` applies defaults (e.g., `bpmn_node_type` fallback).
- **B7 Corpus hash.** SHA-256 hex of the sorted `(triple_id, version)` pairs joined with `\x1f` and `\x1e` record separators.
- **B8 Cache.** Each triple dumped as JSON to `<cache_root>/triples/<corpus_hash>/<safe_filename>.json`. Filenames are sanitised by translating `/\\:*?"<>|` to `_`.

**MDA field mapping (22 mappings).**

| # | Source (MDA) | Target (`Triple`) | Notes |
|---|---|---|---|
| 1 | `capsule_fm.capsule_id` | `triple_id` | required by I1; falls back to directory name if missing |
| 2 | `capsule_fm.version` | `version` | string, default `"0"` |
| 3 | `capsule_fm.bpmn_task_id` | `bpmn_node_id` | required by I1 |
| 4 | `capsule_fm.bpmn_task_type` | `bpmn_node_type` | via `normalize_bpmn_type()` (see table below) |
| 5 | `capsule_fm.regulation_refs[]` | `cim.regulatory_refs[].citation` | each string → `RegulatoryRef(citation=s, rule_text="", obligation_type=REFERENCES)` |
| 6 | `cap_body` `## Business Rules` bullets | `cim.business_rules[]` | `rule_id = "{triple_id}:BR:{NN}"`, `rule_text = stripped bullet` |
| 7 | `intent_fm.goal` | `cim.intent` | trimmed string |
| 8 | `intent_fm.preconditions[]` | `pim.preconditions[]` | each string → `ContextAssertion(path=slugify(s), predicate=EXISTS)` |
| 9 | `intent_fm.inputs[].name` | `pim.state_reads[].path` | |
| 10 | `intent_fm.inputs[].type` | `pim.state_reads[].type` | default `"any"` |
| 11 | `intent_fm.inputs[].source` | `pim.state_reads[].namespace` | |
| 12 | `intent_fm.outputs[].name` | `pim.state_writes[].path` | |
| 13 | `intent_fm.outputs[].type` | `pim.state_writes[].type` | |
| 14 | `intent_fm.outputs[].sink` | `pim.state_writes[].namespace` | |
| 15 | BPMN XML `sequenceFlow[sourceRef=gateway].conditionExpression` | `pim.decision_predicates[].predicate_expression` | only for gateway-typed triples |
| 16 | BPMN XML `sequenceFlow@id` | `pim.decision_predicates[].edge_id` | |
| 17 | BPMN XML `<gateway>@default` | `pim.decision_predicates[].is_default` | true when `flow_id == gw.default` |
| 18 | `cap_body` H2 sections | `psm.enriched_content[]` | one `ContentChunk` per non-empty section |
| 19 | H2 section title | `psm.enriched_content[].chunk_id` | `"{triple_id}:{slug(title)}"` |
| 20 | H2 section title == "regulatory context" | `psm.enriched_content[].content_type = REGULATORY` | else `KNOWLEDGE` |
| 21 | `intent_fm.execution_hints.preferred_agent` | `psm.prompt_scaffold` | |
| 22 | `contract_fm.sources[]` | `psm.tool_bindings[]` | `tool_id=name`, `purpose=protocol`, `mock_response_template=endpoint` |

**`normalize_bpmn_type()` table.** Lowercased input → `BpmnNodeType`:

| MDA type | Mapped |
|---|---|
| `task`, `servicetask`, `usertask`, `businessruletask`, `sendtask`, `receivetask`, `manualtask`, `scripttask` | `TASK` |
| `exclusivegateway`, `inclusivegateway`, `eventbasedgateway` | `EXCLUSIVE_GATEWAY` |
| `parallelgateway` | `PARALLEL_GATEWAY` |
| `startevent` | `START_EVENT` |
| `endevent` | `END_EVENT` |
| `boundaryevent`, `intermediatethrowevent`, `intermediatecatchevent` | `INTERMEDIATE_EVENT` |
| unknown / empty | `TASK` (fallback) |

**Frontmatter parsing.** Regex `\A---\s*\n(.*?)\n---\s*\n?(.*)` with `DOTALL`; body is everything after the closing `---`.

**H2 section splitter.** Lines starting with `## ` begin a section; content before the first `##` is discarded.

**BPMN gateway predicate extraction algorithm.**

1. Parse BPMN XML with `xml.etree.ElementTree`.
2. BPMN namespace: `http://www.omg.org/spec/BPMN/20100524/MODEL`.
3. Find the gateway element by `id`; capture its `default` attribute (default flow id).
4. For every `<bpmn:sequenceFlow>` with `sourceRef == gateway_id`:
   - Read the child `<bpmn:conditionExpression>` text.
   - Strip a `${...}` wrapper if present (regex `^\s*\$\{(.+)\}\s*$`).
   - Emit `BranchPredicate(edge_id=flow_id, predicate_expression=expr, is_default=(flow_id==default_flow_id))`.
   - If a flow has no `conditionExpression` but `flow_id == default`, emit `BranchPredicate(edge_id=flow_id, predicate_expression="default", is_default=True)`.

**Public API.**

```python
class TripleLoader:
    def __init__(self, config: Config) -> None: ...
    def load(self) -> tuple[TripleSet, LoadReport]: ...
    def load_from_cache(self, corpus_version_hash: str) -> TripleSet: ...

# adapter_mda
def discover_triple_dirs(root: Path, ignore_paths: list[str]) -> list[Path]: ...
def load_mda_triple(
    triple_dir: Path,
    bpmn_content: Optional[str] = None,
) -> tuple[Optional[Triple], Optional[dict]]: ...
def normalize_bpmn_type(mda_type: str) -> BpmnNodeType: ...

# adapter_native
def discover_files(root: Path, source_format: str, ignore_paths: list[str]) -> list[Path]: ...
def load_triple(path: Path, source_format: str) -> tuple[Optional[Triple], Optional[dict]]: ...

# normalizer
def validate_identity(triple: Triple) -> list[str]: ...  # missing field names
def normalize(triple: Triple) -> Triple: ...

# source_local
def resolve_local(path: Path) -> Path: ...

# source_git
def clone_or_update(ssh_url: str, branch: str, cache_root: Path) -> Path: ...
```

**Config schema — `config/loader.default.yaml`.**

```yaml
source_format: mda_triple_dir        # or native_yaml | native_json

source:
  type: local                        # or git
  path: ./examples
  # When type=git:
  # ssh_url: git@bitbucket.org:team/triples.git
  # branch: main
  # subdir: triples/

field_mapping: {}                    # reserved

content_chunk_extraction:
  by_section: true                   # split at H2

strict_mode: false                   # unmappable fields preserved under _raw

ignore_paths:
  - .git
  - .cache
  - _manifest.json
```

### 4.2 Component 02 — Triple Inventory

**Purpose.** Apply 10 structural invariants I1-I10 (plus graph-level detections and naming drift) to a `TripleSet`. Produce a completeness matrix, a list of `RawDetection`, an exclusions list, and stats.

**The 10 invariants.** Each module exposes `check(triple_set: TripleSet, graph=None) -> list[RawDetection]`.

| Id | Module | Signal type(s) emitted | Logic |
|---|---|---|---|
| I1 | `i01_identity.py` | `missing_identity_field` | For each triple, collect missing of: `triple_id`, `version` (empty or `"0"`), `bpmn_node_id`. Emit one detection per triple with `detector_context={"missing_fields": [...]}`. |
| I2 | `i02_layer.py` | `missing_layer` | For each triple, for each of `(cim, pim, psm)`, emit a detection if attribute is `None`. `detector_context={"layer_name": "CIM"|"PIM"|"PSM"}`. |
| I3 | `i03_intent.py` | `empty_or_multi_sentence_intent` | `cim.intent` must be non-empty and single-sentence. Multi-sentence detected by regex `[.!?]\s+\S` (a sentence boundary followed by more content). |
| I4 | `i04_contract.py` | `missing_contract_field` | For each triple where `pim is not None`, for each of `preconditions, postconditions, state_reads, state_writes`, emit detection if `getattr(pim, field) is None`. `detector_context={"field_name": "..."}`. |
| I5 | `i05_gateway_predicates.py` | `gateway_missing_predicates` | For triples whose `bpmn_node_type ∈ {EXCLUSIVE_GATEWAY, PARALLEL_GATEWAY}`, emit if `pim.decision_predicates` is falsy. |
| I6 | `i06_obligation_closure.py` | `orphan_obligation` | Two-pass. First pass: collect `closed_ids = ⋃ t.pim.obligations_closed`. Second pass: for each `t.pim.obligations_opened[i]`, emit if `not obligation.exits_journey and obligation.obligation_id not in closed_ids`. |
| I7 | `i07_state_flow.py` | `state_flow_gap` | Gather `writes = ⋃ t.pim.state_writes[].path`. For each triple's `state_reads` and precondition paths, emit a detection if the path is not in `writes`. (Phase 1 uses "any writer anywhere"; reachability filtering reserved for Phase 2.) |
| I8 | `i08_content_presence.py` | `empty_content` | For tasks and gateways, emit if `psm.enriched_content` is empty/missing. Skips triples where `psm is None` (caught by I2). |
| I9 | `i09_predicate_evaluability.py` | `unparseable_predicate` | For each gateway triple's `decision_predicates[i].predicate_expression`, call `ExpressionEvaluator().parse(expr)`; on `ExpressionParseError` emit with `detector_context={"expression": expr, "parse_error": str(e)}` and `bpmn_edge_id` set. The literal `"default"` is always skipped. |
| I10 | `i10_regulatory_resolution.py` | `unresolved_regulatory_ref` | For each `obligation.regulatory_ref` that is non-empty, emit if that citation is not present in `triple.cim.regulatory_refs[].citation`. |

**`invariants/__init__.py`.**

```python
from . import (
    i01_identity, i02_layer, i03_intent, i04_contract, i05_gateway_predicates,
    i06_obligation_closure, i07_state_flow, i08_content_presence,
    i09_predicate_evaluability, i10_regulatory_resolution,
)

INVARIANTS = (
    i01_identity, i02_layer, i03_intent, i04_contract, i05_gateway_predicates,
    i06_obligation_closure, i07_state_flow, i08_content_presence,
    i09_predicate_evaluability, i10_regulatory_resolution,
)
```

**Completeness matrix.** `completeness_matrix.build_matrix(triple_set)` returns a dict keyed by `triple_id` whose value is a per-field booleans dict covering identity fields and PIM contract fields (e.g. `{"cim.intent": True, "pim.preconditions": False, ...}`). `render_markdown(matrix)` renders a `| triple_id | field_a | field_b | ... |` grid using `✓` / `✗`.

**Naming drift detector.** `naming_drift.detect_naming_drift(triple_set)` returns `list[RawDetection]` with `signal_type="naming_drift_suspect"`. Algorithm:

1. Gather all `state_writes` paths (producer) and all `state_reads` paths (consumer) across the corpus.
2. Compute pairwise similarity only for paths that are not identical. Uses a normalized token similarity (e.g. Jaccard on `snake_case`/camelCase-tokenized substrings, normalized to 0..1).
3. Emit one detection per (path_a, path_b) pair with similarity ≥ 0.6 but < 1.0. `detector_context={"path_a", "path_b", "writer_a", "reader_b", "similarity_score"}`.

**`TripleInventory` facade.**

```python
class ExclusionRecord(BaseModel):
    triple_id: str
    reason: str            # "identity_incomplete" | "contract_missing"
    detail: str = ""

class InventoryReport(BaseModel):
    corpus_version_hash: str = ""
    total_triples: int = 0
    completeness_matrix: dict = {}
    raw_detections: list[RawDetection] = []
    exclusions: list[ExclusionRecord] = []
    stats: dict = {}       # { detection_counts, total_detections,
                           #   excluded_triple_count, simulatable_triple_count }
    graph_warning: Optional[str] = None

class TripleInventory:
    def __init__(self, triple_set: TripleSet, graph: Any = None) -> None: ...
    def run(self) -> InventoryReport: ...
    def get_simulation_ready_set(self, report: InventoryReport) -> TripleSet: ...
```

**Exclusion policy.** A triple is excluded when it has any `missing_identity_field` (I1) or any `missing_contract_field` (I4). `get_simulation_ready_set()` returns a TripleSet with those IDs removed.

**Stats block.** Populated by `run()`:

```python
{
    "detection_counts": {signal_type: int},
    "total_detections": int,
    "excluded_triple_count": int,
    "simulatable_triple_count": total - excluded,
}
```

### 4.3 Component 03 — Journey Graph

**Purpose.** Parse a BPMN 2.0 XML file, bind each node to its triple via `bpmn_node_id`, compute reachability and the critical path, and expose a traversal API plus structural detections.

**Phase 1 scope (behavior blocks):** B1 (BPMN parse), B2 (binding), B3 (critical path), B6 (structural checks), B7 (traversal API). Deferred: B4 (derived topology), B5 (cross-validation), full parallel gateway semantics.

**`bpmn_parser.py`.** Parses BPMN XML into:

```python
class BpmnNodeDef(BaseModel):
    node_id: str
    node_type: BpmnNodeType
    name: str = ""
    lane: Optional[str] = None

class BpmnEdgeDef(BaseModel):
    edge_id: str
    source: str
    target: str
    condition: Optional[str] = None
    is_default: bool = False
    name: Optional[str] = None

class BpmnGraphData(BaseModel):
    nodes: dict[str, BpmnNodeDef] = {}
    edges: dict[str, BpmnEdgeDef] = {}
    source_hash: str = ""              # sha256 of the XML bytes
    source_path: str = ""

def parse_bpmn(path: Path) -> BpmnGraphData: ...
```

Namespace-aware: uses `http://www.omg.org/spec/BPMN/20100524/MODEL`. Recognized tags: `task`, `userTask`, `serviceTask`, `businessRuleTask`, `sendTask`, `receiveTask`, `manualTask`, `scriptTask`, `exclusiveGateway`, `parallelGateway`, `inclusiveGateway`, `eventBasedGateway`, `startEvent`, `endEvent`, `boundaryEvent`, `intermediateThrowEvent`, `intermediateCatchEvent`, `sequenceFlow`. Lane names are attached to nodes via `<laneSet><lane><flowNodeRef>`.

**`binder.py`.** `bind(triple_set, bpmn_data) -> tuple[dict[str, Triple], list[RawDetection]]`:

1. Walks `triple_set.triples.values()` and keys them by `triple.bpmn_node_id`.
2. For every BPMN node with no matching triple, emits `RawDetection(signal_type="orphan_bpmn_node", bpmn_node_id=node_id, ...)`.
3. For every triple whose `bpmn_node_id` is not in the BPMN, emits `RawDetection(signal_type="orphan_triple", primary_triple_id=..., detector_context={"reason": "no_matching_bpmn_node"})`.

**`critical_path.py`.** `compute_critical_path(bpmn_data, config_ids: list[str]) -> set[str]`: If `config_ids` is non-empty, those IDs form the critical path. Otherwise, computes the longest simple path from any start event to any end event (using NetworkX on the derived DAG, ignoring back-edges).

**`JourneyGraph` API.**

```python
class JourneyGraph:
    def __init__(
        self,
        bpmn_data: BpmnGraphData,
        triple_set: TripleSet,
        critical_path_ids: Optional[set[str]] = None,
    ): ...

    @classmethod
    def from_bpmn_file(
        cls,
        bpmn_path: Path,
        triple_set: TripleSet,
        config_critical_path: Optional[list[str]] = None,
    ) -> "JourneyGraph": ...

    # Traversal
    def start_events(self) -> list[str]: ...
    def end_events(self) -> list[str]: ...
    def successors(self, node_id: str) -> list[str]: ...
    def predecessors(self, node_id: str) -> list[str]: ...
    def edges_from(self, node_id: str) -> list[dict]:
        # [{edge_id, target, condition, is_default, name}]
        ...
    def is_reachable(self, from_node: str, to_node: str) -> bool: ...
    def all_paths(self, from_node: str, to_node: str,
                  max_depth: int = 100) -> list[list[str]]: ...
    def pairs_to_check(self) -> list[tuple[str, str]]: ...  # all direct edges
    def get_triple(self, node_id: str) -> Optional[Triple]: ...
    def get_node(self, node_id: str) -> Optional[dict]: ...
    def is_on_critical_path(self, node_id: str) -> bool: ...

    # Properties
    @property
    def detections(self) -> list[RawDetection]: ...     # binding + structural
    @property
    def bpmn_data(self) -> BpmnGraphData: ...
    @property
    def bindings(self) -> dict[str, Triple]: ...
    @property
    def critical_path(self) -> set[str]: ...
    @property
    def networkx(self) -> nx.DiGraph: ...
```

**Orphan detection via reachability (`_structural_checks`).** Run during construction:

1. Collect all start-event node IDs.
2. `reachable = ⋃ (start ∪ nx.descendants(G, start))`.
3. For every bound node not in `reachable`, emit `orphan_triple` with `detector_context={"reason": "unreachable_from_start"}`.
4. For every non-end-event node with `out_degree == 0`, emit `orphan_triple` with `detector_context={"reason": "dead_end"}`.

Detections are exposed via the `detections` property so `TripleInventory.run()` can consume them.

### 4.4 Component 11 — Finding Classifier

**Purpose.** Convert `RawDetection` → `Finding` by mapping `signal_type` through `rules.yaml`, rendering summary/detail strings via Jinja2, and computing a stable dedup key.

**`rules.yaml` structure.**

```yaml
taxonomy_version: "1.0.0"

rules:
  <signal_type>:
    defect_class: <enum_value>
    layer: <"CIM"|"PIM"|"PSM"|"N/A"|"{layer_name}">  # may be a template
    severity: <enum>                                   # default correctness
    confidence: <enum>                                 # default high
    summary_template: <jinja>
    detail_template: <jinja>
```

The layer field can be a Jinja expression (e.g. `"{layer_name}"`), in which case it is resolved with the detector context first, then enum-cast (falls back to `N/A` on failure).

**All 13 rules.** The mappings below are the verbatim contents of `rules.yaml`:

| signal_type | defect_class | layer | severity | confidence |
|---|---|---|---|---|
| `missing_identity_field` | `identity_incomplete` | `N/A` | correctness | high |
| `missing_layer` | `layer_missing` | `{layer_name}` | correctness | high |
| `empty_or_multi_sentence_intent` | `content_missing` | `CIM` | correctness | high |
| `missing_contract_field` | `contract_missing` | `PIM` | correctness | high |
| `gateway_missing_predicates` | `evaluability_gap` | `PIM` | correctness | high |
| `orphan_obligation` | `orphan_obligation` | `PIM` | correctness | high |
| `state_flow_gap` | `state_flow_gap` | `PIM` | correctness | high |
| `empty_content` | `content_missing` | `PSM` | correctness | high |
| `unparseable_predicate` | `evaluability_gap` | `PIM` | correctness | high |
| `unresolved_regulatory_ref` | `regulatory_orphan` | `CIM` | correctness | high |
| `orphan_triple` | `orphan_triple` | `PIM` | correctness | high |
| `orphan_bpmn_node` | `orphan_triple` | `PIM` | correctness | medium |
| `naming_drift_suspect` | `handoff_naming_drift` | `PIM` | cosmetic | low |

(Full rules.yaml with templates reproduced in Appendix A.)

**`templates.py`.** Thin Jinja2 wrapper:

```python
from jinja2 import Environment, BaseLoader, StrictUndefined

_env = Environment(
    loader=BaseLoader(),
    undefined=StrictUndefined,  # but actually caller uses lenient rendering; see below
    keep_trailing_newline=False,
    autoescape=False,
)

def render(template_str: str, context: dict) -> str:
    """Render a Jinja template. On missing key, substitute an empty string
    rather than raising, so partial detector contexts don't crash the
    classifier."""
    ...
```

In practice `render` swaps to a lenient `Undefined` (rather than strict) because detector contexts are heterogeneous. The function also tolerates Python-style `{foo}` substitution as a fallback when a string contains no Jinja `{% %}` or `{{ }}` markers.

**Dedup key algorithm.** Both `FindingClassifier.dedup_key(finding)` and `store.compute_dedup_key()` compute:

```
sha256( "|".join([
    defect_class.value,
    primary_triple_id or "",
    bpmn_edge_id or "",
    json.dumps(observed, sort_keys=True, default=str, ensure_ascii=False),
]))  -> hex digest
```

`observed` is `finding.evidence.observed`. The canonical JSON serialization guarantees stable dedup across runs.

**Public API.**

```python
class FindingClassifier:
    def __init__(self, rules_path: Optional[Path] = None, strict: bool = True): ...
    def classify(self, detection: RawDetection, run_id: str) -> Finding: ...
    def dedup_key(self, finding: Finding) -> str: ...
    # Internals: _build_context(detection) -> dict, _fallback(detection, run_id) -> Finding
```

**Fallback behavior.** When `strict=True` and a signal has no rule, raise `ValueError`. When `strict=False` (as used by the CLI), emit a `Finding` with `defect_class=CONTENT_MISSING`, `layer=N/A`, `confidence=LOW`, `summary=f"Unclassified signal: {signal_type}"`.

### 4.5 Component 12 — Finding Store

**Purpose.** SQLite-backed persistence for runs and findings with stable dedup.

**Complete SQL schema (`schema.sql`).**

```sql
-- Finding store schema (SQLite).
-- Spec reference: files/12-finding-store.md

CREATE TABLE IF NOT EXISTS runs (
    run_id TEXT PRIMARY KEY,
    started_at TEXT NOT NULL,
    completed_at TEXT,
    corpus_version_hash TEXT,
    bpmn_version_hash TEXT,
    generator TEXT,
    simulator_version TEXT,
    taxonomy_version TEXT,
    config_json TEXT,
    status TEXT DEFAULT 'running',   -- running/completed/failed
    metrics_json TEXT
);

CREATE TABLE IF NOT EXISTS findings (
    finding_id TEXT PRIMARY KEY,
    dedup_key TEXT NOT NULL,
    taxonomy_version TEXT NOT NULL,
    layer TEXT NOT NULL,
    defect_class TEXT NOT NULL,
    generator TEXT NOT NULL,
    severity TEXT NOT NULL,
    confidence TEXT NOT NULL,
    primary_triple_id TEXT,
    related_triple_ids TEXT,         -- JSON array
    bpmn_node_id TEXT,
    bpmn_edge_id TEXT,
    summary TEXT NOT NULL,
    detail TEXT,
    evidence_json TEXT,
    journeys_affected_count INTEGER DEFAULT 0,
    journeys_affected_pct REAL DEFAULT 0.0,
    is_on_critical_path INTEGER DEFAULT 0,
    status TEXT DEFAULT 'new',
    suppression_reason TEXT,
    first_seen_run TEXT NOT NULL,
    last_seen_run TEXT NOT NULL,
    occurrence_count INTEGER DEFAULT 1,
    first_detected_at TEXT NOT NULL,
    last_detected_at TEXT NOT NULL
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_findings_dedup     ON findings(dedup_key);
CREATE INDEX        IF NOT EXISTS idx_findings_triple    ON findings(primary_triple_id);
CREATE INDEX        IF NOT EXISTS idx_findings_class     ON findings(defect_class);
CREATE INDEX        IF NOT EXISTS idx_findings_generator ON findings(generator);

CREATE TABLE IF NOT EXISTS finding_occurrences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    finding_id TEXT NOT NULL REFERENCES findings(finding_id),
    run_id TEXT NOT NULL REFERENCES runs(run_id),
    detected_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_occurrences_finding ON finding_occurrences(finding_id);
CREATE INDEX IF NOT EXISTS idx_occurrences_run     ON finding_occurrences(run_id);
```

**`PRAGMA foreign_keys = ON` is enabled on connection open.**

**Public API.**

```python
def compute_dedup_key(
    defect_class: str,
    primary_triple_id: Optional[str],
    bpmn_edge_id: Optional[str],
    observed: Any,
) -> str: ...

class FindingStore:
    def __init__(self, db_path: Path) -> None: ...       # init schema on open
    def start_run(
        self,
        run_id: str,
        corpus_version_hash: str,
        bpmn_version_hash: str,
        generator: str,
        simulator_version: str,
        taxonomy_version: str,
        config: dict,
    ) -> None: ...
    def complete_run(self, run_id: str, metrics: dict) -> None: ...
    def fail_run(self, run_id: str, error: str) -> None: ...

    def emit_finding(self, finding: Finding, run_id: str) -> str: ...
        # returns finding_id; dedups by dedup_key.

    def get_findings(self, **filters: Any) -> list[Finding]: ...
        # allowed filters: defect_class, layer, generator, severity, confidence,
        # primary_triple_id, bpmn_node_id, bpmn_edge_id, status.
    def findings_by_triple(self, triple_id: str) -> list[Finding]: ...
    def findings_by_class(self, defect_class: str | DefectClass) -> list[Finding]: ...
    def findings_by_run(self, run_id: str) -> list[Finding]: ...

    def close(self) -> None: ...
```

**Dedup behavior.** On `emit_finding`:

1. Compute `dedup_key`.
2. SELECT by key.
3. If existing: UPDATE `occurrence_count = existing + 1`, set `last_seen_run`, `last_detected_at`. Do **not** overwrite `summary`, `detail`, `evidence_json`.
4. If new: INSERT full row.
5. Always INSERT one row into `finding_occurrences` (one per emission).

**Phase 1 scope notes (from store module docstring).** Phase 1 implements the first 4 bullets only:

- start_run / complete_run / fail_run ✓
- emit_finding with dedup ✓
- get_findings / findings_by_triple / findings_by_class / findings_by_run ✓
- **Deferred (Phase 4):** blast radius, lifecycle transitions (triage/accept/suppress/resolve/regress), retention/pruning, regression detection via trace diff.

### 4.6 Expression Evaluator

**Purpose.** Parse decision-predicate expressions. Phase 1 is **parse-only**; evaluation arrives in Phase 2.

**Full `grammar.lark`.**

```lark
// Expression grammar for triple decision predicates.
// Spec reference: files/04-static-handoff-checker.md §B4
//
// Phase 1 scope: parse-only. Evaluation comes in later phases.

start: expr

?expr: or_expr

or_expr: and_expr (OR and_expr)*
and_expr: not_expr (AND not_expr)*

?not_expr: NOT not_expr       -> not_op
         | membership
         | compare

// Membership: "x in [...]" or "x not in [...]"
membership: addition IN list_literal         -> in_op
          | addition NOT IN list_literal     -> not_in_op

compare: addition (COMP_OP addition)?

?addition: atom

?atom: func_call
     | path
     | literal
     | list_literal
     | "(" expr ")"

func_call: NAME "(" [args] ")"
args: arg ("," arg)*
?arg: NAME "=" expr    -> kwarg
    | expr             -> posarg

path: NAME ("." NAME)*

literal: STRING             -> str_lit
       | SIGNED_NUMBER      -> num_lit
       | TRUE               -> true_lit
       | FALSE              -> false_lit
       | NULL               -> null_lit

list_literal: "[" [expr ("," expr)*] "]"

// Keywords (terminals so they don't collide with NAME).
AND: /and\b/
OR: /or\b/
NOT: /not\b/
IN: /in\b/
TRUE: /true\b/
FALSE: /false\b/
NULL: /null\b/

COMP_OP: "==" | "!=" | "<=" | ">=" | "<" | ">"

NAME: /(?!(?:and|or|not|in|true|false|null)\b)[a-zA-Z_][a-zA-Z0-9_]*/
STRING: /"(?:[^"\\]|\\.)*"/ | /'(?:[^'\\]|\\.)*'/

%import common.SIGNED_NUMBER
%import common.WS
%ignore WS
```

**AST nodes (`ast_nodes.py`).** Pydantic models, all `extra="allow"`. Minimum set:

- `BoolOp(op: str, operands: list[Node])` — `op ∈ {"and","or"}`
- `NotOp(operand: Node)`
- `Compare(left: Node, op: str, right: Optional[Node])` — `op ∈ {"==","!=","<=",">=","<",">"}`
- `InOp(left: Node, right: Node, negated: bool)`
- `FuncCall(name: str, args: list[Node], kwargs: dict[str, Node])`
- `Path(parts: list[str])`  // e.g. `foo.bar.baz`
- `StrLit(value: str)`, `NumLit(value: float)`, `BoolLit(value: bool)`, `NullLit()`
- `ListLit(values: list[Node])`

**`parser.py`.** `ExpressionEvaluator.parse(expression: str) -> ParseResult`.

```python
class ExpressionParseError(Exception):
    ...

class ParseResult(BaseModel):
    expression: str
    ast: Any           # root AST node
    referenced_paths: list[str] = []   # every Path seen in the tree (dot-joined)
    referenced_funcs: list[str] = []   # every FuncCall name

class ExpressionEvaluator:
    def __init__(self, grammar_path: Optional[Path] = None): ...  # loads grammar.lark
    def parse(self, expression: str) -> ParseResult: ...          # raises on error
    # Phase 2: def evaluate(self, expression, context) -> Any
```

`parse()` uses `lark.Lark(...).parse(expression)`, then a `Transformer` walks the tree to build the AST and accumulate `referenced_paths` / `referenced_funcs`. Any Lark error is wrapped in `ExpressionParseError`.

---

## 5. CLI

**Entry points.** `python -m triple_flow_sim <command>` (via `if __name__ == "__main__"` in `cli.py`) or the console script `triple_flow_sim` installed by `pip install -e .` (registered under `[project.scripts]`).

**Root group.** `@click.group()` with `--version` option using `__version__`.

**Command tree.**

```
triple_flow_sim
  --version

triple_flow_sim inventory
  --corpus-config PATH   (required; path to loader YAML)
  --bpmn PATH            (optional; BPMN 2.0 XML)
  --out DIR              (default: ./reports)
  --log-level [DEBUG|INFO|WARNING|ERROR]   (default: INFO)

triple_flow_sim load
  --corpus-config PATH   (required)
```

**Pipeline wiring (inventory command).**

1. `run_id = utcnow().strftime("%Y%m%dT%H%M%S") + "-" + uuid4().hex[:8]`; `run_dir = out / run_id`.
2. `config = load_config(corpus_config)` (merges default + user YAML).
3. `loader = TripleLoader(config); triple_set, load_report = loader.load()`.
4. If `--bpmn` given: `graph = JourneyGraph.from_bpmn_file(bpmn_path, triple_set)`; else `graph = None` and a warning is logged.
5. `store = FindingStore(run_dir / "findings.db"); store.start_run(run_id, corpus_version_hash, bpmn_hash, "inventory", simulator_version, TAXONOMY_VERSION, config.to_dict())`.
6. `inv = TripleInventory(triple_set, graph=graph); report = inv.run()`.
7. `classifier = FindingClassifier(strict=False)`; for each `det in report.raw_detections`: `store.emit_finding(classifier.classify(det, run_id), run_id)`.
8. `store.complete_run(run_id, metrics={total_triples, total_findings, excluded_triples}); store.close()`.
9. `write_reports(report, findings, run_id, run_dir)` — produces `inventory.md` and `inventory.json`.
10. Print a banner to stdout summarizing run id, triples loaded, findings emitted, exclusions, report directory. Return 0.

**`main()` error handling.** Wraps `cli(standalone_mode=False)`; catches `click.Abort` → return 1, `click.ClickException` → print and return exit code.

---

## 6. Reports

### 6.1 Markdown report (`inventory.md`)

Section order:

1. **Header** — `# Triple Flow Simulator — Inventory Report`, then list of: Run ID, Generated at (UTC ISO), Corpus version hash, Total triples, Findings count, Simulatable triples, Excluded triples.
2. **Summary** — table `| signal_type | count |` sorted descending by count. Empty state: `*(no detections)*`.
3. **Exclusions** — table `| triple_id | reason | detail |`. Empty state: `*(none)*`.
4. **Findings** — grouped by `defect_class`, most common first. Each class has a `### <class> (N)` heading and a bullet per finding: `- \`{primary_triple_id}\` — {summary}`.
5. **Completeness Matrix** — rendered via `completeness_matrix.render_markdown()`.
6. **Graph Status** — only when `report.graph_warning` is set; prints the warning verbatim.

### 6.2 JSON report (`inventory.json`)

Top-level keys:

```json
{
  "run_id": "...",
  "generated_at": "<UTC ISO>Z",
  "corpus_version_hash": "...",
  "total_triples": 8,
  "stats": {
    "detection_counts": {...},
    "total_detections": 52,
    "excluded_triple_count": 8,
    "simulatable_triple_count": 0
  },
  "exclusions": [{"triple_id": "...", "reason": "...", "detail": "..."}],
  "completeness_matrix": {...},
  "findings": [ <Finding.model_dump(mode="json")>, ... ],
  "graph_warning": "..." | null
}
```

### 6.3 `write_reports` API

```python
def render_markdown_report(report: InventoryReport,
                           findings: list[Finding], run_id: str) -> str: ...
def render_json_report(report: InventoryReport,
                       findings: list[Finding], run_id: str) -> dict: ...
def write_reports(report: InventoryReport,
                  findings: list[Finding],
                  run_id: str,
                  out_dir: Path) -> dict:
    # returns {"markdown_path": Path, "json_path": Path}
```

---

## 7. Test Strategy

All tests live under `tests/`.

**Fixture directories.**

- `tests/fixtures/corpus_clean/` — a well-formed MDA-format corpus that produces zero I1/I4 exclusions. Used to verify that a good corpus returns a mostly-empty finding set.
- `tests/fixtures/corpus_seeded/` — the same corpus with deliberate defects seeded (missing contract fields, gateway with no predicates, orphan obligation, etc.). Each seeded defect is documented in a sidecar `README.md` and each expected finding has a test assertion.
- `tests/fixtures/bpmn/` — synthetic BPMN XML for graph-binding tests: one happy-path flow, one with an unreachable node, one with a dead-end node, and one with a gateway that has a `${...}` condition expression.

**Unit tests (tests/unit/).**

- `c01/` — adapter_mda parses cap/intent/contract correctly; gateway predicate extraction from BPMN XML; identity validation; corpus hash stability.
- `c02/` — one file per invariant (`test_i01.py` … `test_i10.py`) plus `test_inventory_facade.py`, `test_completeness_matrix.py`, `test_naming_drift.py`.
- `c03/` — `test_bpmn_parser.py`, `test_binder.py`, `test_graph.py` (reachability, successors, edges_from, critical path, orphan emission).
- `c11/` — classifier matches each signal type to correct defect_class/layer/severity, template renders, dedup_key is stable, fallback (non-strict) path.
- `c12/` — schema init, emit_finding/dedup, occurrences on re-emit, get_findings filters, findings_by_run.
- `evaluator/` — valid expressions parse (paths, equality, in/not-in, function calls, nested boolean, string and number literals); invalid expressions raise `ExpressionParseError`.

**Integration tests (tests/integration/).**

- `test_inventory_e2e.py` — Run the CLI programmatically against `corpus_seeded` + a BPMN fixture, assert exit 0, expected finding counts per defect_class, `findings.db` row counts, `inventory.md` contains expected headers, `inventory.json` schema matches.

**Total: 86 passing tests.**

---

## 8. Verification

```bash
cd triple-flow-sim
pip install -e .[dev]

# All tests must pass.
pytest tests/
# Expected: 86 passed

# Run against the examples/income-verification MDA corpus.
python -m triple_flow_sim inventory \
    --corpus-config config/mda-income-verification.yaml \
    --bpmn ../examples/income-verification/bpmn/income-verification.bpmn \
    --out reports/
```

**Expected outcome on `examples/income-verification`:**

- 8 triples loaded.
- ~50+ findings, dominated by `contract_missing` and `state_flow_gap` (because the example corpus uses the MDA format which does not natively populate all PIM contract fields).
- All 8 triples appear in the `Exclusions` section with reason `contract_missing` → zero simulatable triples (expected for Phase 1 on an untreated real corpus).
- Exit code 0.

---

## 9. Phase 1 Acceptance Criteria

| # | Criterion | Verification |
|---|---|---|
| 1 | CLI runs end-to-end against a real corpus with exit 0 | `python -m triple_flow_sim inventory ...` on `examples/income-verification` |
| 2 | Seeded defects detected with correct `defect_class` | Integration test on `corpus_seeded` |
| 3 | Inventory report readable without engineering help | Manual review of `inventory.md` — sections labeled, triple IDs and paths exposed |
| 4 | Deterministic across runs | Running twice on the same corpus produces identical `corpus_version_hash` and identical `dedup_key`s; findings table row count is stable |
| 5 | Every component's V1-V7 unit verifications pass | `pytest tests/unit/` green |

---

## 10. What Phase 1 Does NOT Deliver

- **No LLM calls.** The evaluator, classifier, and report paths are entirely static. Grounded checking is Phase 3.
- **No pairwise static handoff conformance.** `component 04` (`static_handoff_checker`) is Phase 2.
- **No context isolation harness.** This is the keystone Phase 3 diagnostic: does a triple succeed with only its declared context vs. full ambient context?
- **No generators suite.** Sequence runner, branch-boundary, perturbation, ablation, and volume generators are Phase 4.
- **No triage / accept / suppress / resolve lifecycle.** `FindingStore` only supports `NEW`; lifecycle transitions land in Phase 4.
- **No blast radius computation.** `journeys_affected_*` and `is_on_critical_path` are written as 0 / false in Phase 1.

---

## 11. Cross-Phase Discipline Applied

From `files/99-task-breakdown.md §"Cross-phase discipline"`:

1. **Every task has inline verification.** Each invariant has a unit test; the CLI has an integration test.
2. **Unit tests per component.** `tests/unit/c{01,02,03,11,12}/` and `tests/unit/evaluator/`.
3. **Findings are traced.** `Finding.first_seen_run`, `last_seen_run`, `occurrence_count` tie every finding back to a run.
4. **Config externalized.** `config/loader.default.yaml` plus user YAML; no hardcoded corpus paths.
5. **Taxonomy version on every finding.** `Finding.taxonomy_version = "1.0.0"`, also stamped on each row in `findings` and `runs`.
6. **Module docstrings reference specs.** Every module top-of-file docstring includes `Spec reference: files/<nn>-<name>.md`.

---

## 12. Installation and First Run

```bash
cd triple-flow-sim
pip install -e .
pytest tests/
```

**Creating a loader config for your corpus (git source):**

```yaml
# my-corpus.yaml
source_format: mda_triple_dir
source:
  type: git
  ssh_url: git@bitbucket.org:your-team/triples.git
  branch: main
  subdir: triples/
content_chunk_extraction:
  by_section: true
strict_mode: false
ignore_paths:
  - .git
  - .cache
```

**Or local:**

```yaml
source_format: mda_triple_dir
source:
  type: local
  path: /absolute/path/to/triples/root
content_chunk_extraction:
  by_section: true
strict_mode: false
```

**Then:**

```bash
python -m triple_flow_sim inventory \
    --corpus-config my-corpus.yaml \
    --bpmn path/to/process.bpmn \
    --out reports/
```

---

## 13. Forward Compatibility

Phase 1 builds the full contract models (`Finding`, `Trace`, `IsolationResult`, `JourneyContext`, etc.) even though Phase 1 only populates a subset. Implications:

- **Phase 2** plugs in `static_handoff_checker` without model changes — it emits `RawDetection(generator=STATIC_HANDOFF, ...)` and the existing classifier+store path handles persistence.
- **Phase 3** plugs in LLM-backed generators (`grounded_pair`, `context_isolation`) without changing the store or classifier — new rules in `rules.yaml` cover the new signal types.
- **Phase 4** completes the store (lifecycle, blast radius, retention), adds the sequence runner, and ships the report suite.

The `taxonomy_version = "1.0.0"` on every finding enables per-phase migration: when the enum changes, bump the version; `findings.taxonomy_version` lets older rows still be interpreted correctly.

---

## 14. File-by-File Inventory

| Path | Purpose |
|---|---|
| `pyproject.toml` | Package metadata, deps, package-data declarations (rules.yaml, schema.sql, grammar.lark), console script |
| `README.md` | Project overview and quick start |
| `config/loader.default.yaml` | Default loader config, merged under user config |
| `triple_flow_sim/__init__.py` | `__version__`, `TAXONOMY_VERSION` |
| `triple_flow_sim/cli.py` | Click entry; `inventory` and `load` commands; pipeline wiring |
| `triple_flow_sim/config.py` | YAML loader with deep merge + dotted-key accessor |
| `triple_flow_sim/logging_setup.py` | `setup_logging`, `get_logger` (stderr) |
| `triple_flow_sim/contracts/__init__.py` | Re-exports of public contract types |
| `triple_flow_sim/contracts/triple.py` | `Triple`, layer classes, `TripleSet`, `LoadReport`, enums |
| `triple_flow_sim/contracts/finding.py` | `Finding`, `RawDetection`, taxonomy enums |
| `triple_flow_sim/contracts/journey_context.py` | Phase-3 stub models (built now for fwd-compat) |
| `triple_flow_sim/contracts/trace.py` | Phase-2/3 stub models |
| `triple_flow_sim/evaluator/__init__.py` | `ExpressionEvaluator` export |
| `triple_flow_sim/evaluator/grammar.lark` | Predicate grammar (parse-only in Phase 1) |
| `triple_flow_sim/evaluator/parser.py` | Lark wrapper + Transformer → AST |
| `triple_flow_sim/evaluator/ast_nodes.py` | Pydantic AST node models |
| `triple_flow_sim/components/c01_loader/__init__.py` | `TripleLoader` export |
| `triple_flow_sim/components/c01_loader/loader.py` | Facade; pipeline B1-B8 |
| `triple_flow_sim/components/c01_loader/adapter_mda.py` | MDA format adapter (cap/intent/contract → Triple) |
| `triple_flow_sim/components/c01_loader/adapter_native.py` | Native YAML/JSON adapter |
| `triple_flow_sim/components/c01_loader/normalizer.py` | `validate_identity`, `normalize` |
| `triple_flow_sim/components/c01_loader/source_local.py` | Local path resolver |
| `triple_flow_sim/components/c01_loader/source_git.py` | Git clone/pull into cache |
| `triple_flow_sim/components/c02_inventory/__init__.py` | `TripleInventory`, `InventoryReport` exports |
| `triple_flow_sim/components/c02_inventory/inventory.py` | Facade — runs all invariants + graph detections + drift |
| `triple_flow_sim/components/c02_inventory/completeness_matrix.py` | `build_matrix`, `render_markdown` |
| `triple_flow_sim/components/c02_inventory/naming_drift.py` | Token-similarity-based naming-drift detector |
| `triple_flow_sim/components/c02_inventory/invariants/__init__.py` | `INVARIANTS = (i01_identity, ..., i10_regulatory_resolution)` |
| `triple_flow_sim/components/c02_inventory/invariants/i01_identity.py` | I1 — identity fields |
| `triple_flow_sim/components/c02_inventory/invariants/i02_layer.py` | I2 — cim/pim/psm present |
| `triple_flow_sim/components/c02_inventory/invariants/i03_intent.py` | I3 — single-sentence intent |
| `triple_flow_sim/components/c02_inventory/invariants/i04_contract.py` | I4 — PIM contract fields declared |
| `triple_flow_sim/components/c02_inventory/invariants/i05_gateway_predicates.py` | I5 — gateways declare predicates |
| `triple_flow_sim/components/c02_inventory/invariants/i06_obligation_closure.py` | I6 — obligations closed |
| `triple_flow_sim/components/c02_inventory/invariants/i07_state_flow.py` | I7 — reads match writes |
| `triple_flow_sim/components/c02_inventory/invariants/i08_content_presence.py` | I8 — content chunks present |
| `triple_flow_sim/components/c02_inventory/invariants/i09_predicate_evaluability.py` | I9 — predicates parse |
| `triple_flow_sim/components/c02_inventory/invariants/i10_regulatory_resolution.py` | I10 — obligation regulatory_ref resolves |
| `triple_flow_sim/components/c03_graph/__init__.py` | `JourneyGraph` export |
| `triple_flow_sim/components/c03_graph/graph.py` | `JourneyGraph` — traversal + structural checks |
| `triple_flow_sim/components/c03_graph/bpmn_parser.py` | `parse_bpmn` → `BpmnGraphData` |
| `triple_flow_sim/components/c03_graph/binder.py` | Bind triples to BPMN nodes |
| `triple_flow_sim/components/c03_graph/critical_path.py` | `compute_critical_path` |
| `triple_flow_sim/components/c11_classifier/__init__.py` | `FindingClassifier` export |
| `triple_flow_sim/components/c11_classifier/classifier.py` | Signal → Finding mapping |
| `triple_flow_sim/components/c11_classifier/templates.py` | Jinja2 renderer (lenient undefined) |
| `triple_flow_sim/components/c11_classifier/rules.yaml` | 13 signal-type mappings |
| `triple_flow_sim/components/c12_store/__init__.py` | `FindingStore` export |
| `triple_flow_sim/components/c12_store/store.py` | SQLite CRUD with dedup |
| `triple_flow_sim/components/c12_store/schema.sql` | Tables: runs, findings, finding_occurrences + indexes |
| `triple_flow_sim/reports/__init__.py` | (empty) |
| `triple_flow_sim/reports/inventory_report.py` | Markdown + JSON report renderers |

---

## Appendix A — Full `rules.yaml`

```yaml
taxonomy_version: "1.0.0"

rules:
  missing_identity_field:
    defect_class: identity_incomplete
    layer: "N/A"
    severity: correctness
    confidence: high
    summary_template: "Triple {primary_triple_id} missing identity field(s): {missing_fields}"
    detail_template: |
      Identity fields are required by invariant I1 (files/triple-schema.md).
      Missing: {missing_fields}
      Source path: {source_path}
      This triple is excluded from downstream simulation.

  missing_layer:
    defect_class: layer_missing
    layer: "{layer_name}"
    severity: correctness
    confidence: high
    summary_template: "Triple {primary_triple_id} is missing the {layer_name} layer"
    detail_template: |
      Invariant I2 (files/triple-schema.md) requires cim, pim, and psm layers.
      Missing layer: {layer_name}

  empty_or_multi_sentence_intent:
    defect_class: content_missing
    layer: CIM
    severity: correctness
    confidence: high
    summary_template: "Triple {primary_triple_id} has empty or non-single-sentence cim.intent"
    detail_template: |
      Invariant I3 (files/triple-schema.md) requires cim.intent to be a single sentence.
      Observed: {observed_intent}

  missing_contract_field:
    defect_class: contract_missing
    layer: PIM
    severity: correctness
    confidence: high
    summary_template: "Triple {primary_triple_id} missing contract field: {field_name}"
    detail_template: |
      Invariant I4 (files/triple-schema.md) requires pim.preconditions, pim.postconditions,
      pim.state_reads, and pim.state_writes to be declared (may be empty lists but must exist).
      Missing: {field_name}
      This triple is excluded from downstream simulation.

  gateway_missing_predicates:
    defect_class: evaluability_gap
    layer: PIM
    severity: correctness
    confidence: high
    summary_template: "Gateway triple {primary_triple_id} lacks pim.decision_predicates"
    detail_template: |
      Invariant I5 (files/triple-schema.md) requires gateways to declare decision_predicates.
      bpmn_node_type: {bpmn_node_type}

  orphan_obligation:
    defect_class: orphan_obligation
    layer: PIM
    severity: correctness
    confidence: high
    summary_template: "Obligation {obligation_id} opened by {primary_triple_id} but never closed"
    detail_template: |
      Invariant I6 (files/triple-schema.md) requires every opened obligation to be closed
      on some path or explicitly marked exits_journey=true.
      Opened by: {primary_triple_id}
      Obligation: {obligation_id}
      Description: {obligation_description}

  state_flow_gap:
    defect_class: state_flow_gap
    layer: PIM
    severity: correctness
    confidence: high
    summary_template: "Triple {primary_triple_id} reads '{path}' which no upstream triple writes"
    detail_template: |
      Invariant I7 (files/triple-schema.md) requires read paths to be written by some
      upstream triple reachable in the journey graph.
      Read path: {path}
      Reader: {primary_triple_id}

  empty_content:
    defect_class: content_missing
    layer: PSM
    severity: correctness
    confidence: high
    summary_template: "Triple {primary_triple_id} has empty psm.enriched_content"
    detail_template: |
      Invariant I8 (files/triple-schema.md) requires task and gateway nodes to have non-empty
      enriched_content.
      bpmn_node_type: {bpmn_node_type}

  unparseable_predicate:
    defect_class: evaluability_gap
    layer: PIM
    severity: correctness
    confidence: high
    summary_template: "Predicate unparseable on edge {bpmn_edge_id}: {parse_error}"
    detail_template: |
      Invariant I9 (files/triple-schema.md) requires decision_predicates to be parseable
      by the expression evaluator.
      Expression: {expression}
      Error: {parse_error}
      Gateway: {primary_triple_id}

  unresolved_regulatory_ref:
    defect_class: regulatory_orphan
    layer: CIM
    severity: correctness
    confidence: high
    summary_template: "Regulatory ref '{citation}' in {primary_triple_id} not declared in cim.regulatory_refs"
    detail_template: |
      Invariant I10 (files/triple-schema.md) requires every obligation's regulatory_ref
      to resolve to an entry in cim.regulatory_refs.
      Obligation: {obligation_id}
      Unresolved ref: {citation}

  orphan_triple:
    defect_class: orphan_triple
    layer: PIM
    severity: correctness
    confidence: high
    summary_template: "Triple {primary_triple_id} is not reachable from any start event"
    detail_template: |
      This triple is bound to BPMN node {bpmn_node_id} but that node is unreachable
      from any start event in the journey graph.

  orphan_bpmn_node:
    defect_class: orphan_triple
    layer: PIM
    severity: correctness
    confidence: medium
    summary_template: "BPMN node {bpmn_node_id} has no bound triple"
    detail_template: |
      The BPMN graph contains a node with no triple in the corpus that references it via
      bpmn_node_id. Either the triple is missing, or the BPMN has been updated without
      triple authoring.

  naming_drift_suspect:
    defect_class: handoff_naming_drift
    layer: PIM
    severity: cosmetic
    confidence: low
    summary_template: "Possible naming drift: {path_a} vs {path_b}"
    detail_template: |
      Two state paths appear semantically related but are syntactically different.
      This may indicate handoff naming drift where producer and consumer disagree on spelling.
      Path A: {path_a} (written by {writer_a})
      Path B: {path_b} (read by {reader_b})
      Similarity: {similarity_score}
```

---

## Appendix B — Example `pyproject.toml`

```toml
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "triple_flow_sim"
version = "0.1.0"
description = "Diagnostic simulator for inter-triple handoffs in MDA Intent Layer processes"
readme = "README.md"
requires-python = ">=3.10"
license = { text = "MIT" }
authors = [ { name = "Triple Flow Simulator Team" } ]
classifiers = [
    "Development Status :: 3 - Alpha",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Programming Language :: Python :: 3.13",
    "License :: OSI Approved :: MIT License",
]
dependencies = [
    "pyyaml>=6.0",
    "pydantic>=2.0",
    "networkx>=3.0",
    "click>=8.0",
    "lark>=1.1",
    "gitpython>=3.1",
    "jinja2>=3.1",
]

[project.optional-dependencies]
dev = ["pytest>=8.0", "pytest-cov>=4.0"]

[project.scripts]
triple_flow_sim = "triple_flow_sim.cli:main"

[tool.setuptools.packages.find]
include = ["triple_flow_sim*"]

[tool.setuptools.package-data]
triple_flow_sim = [
    "components/c11_classifier/rules.yaml",
    "components/c12_store/schema.sql",
    "evaluator/grammar.lark",
]

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
addopts = "-v"
```

---

## Appendix C — BPMN parsing cheat sheet

- **Namespace.** All elements live under `{http://www.omg.org/spec/BPMN/20100524/MODEL}`.
- **Recognized flow-node tags.** `task`, `userTask`, `serviceTask`, `businessRuleTask`, `sendTask`, `receiveTask`, `manualTask`, `scriptTask`, `exclusiveGateway`, `parallelGateway`, `inclusiveGateway`, `eventBasedGateway`, `startEvent`, `endEvent`, `boundaryEvent`, `intermediateThrowEvent`, `intermediateCatchEvent`.
- **Edges.** `sequenceFlow` with `id`, `sourceRef`, `targetRef`. Optional child `conditionExpression` text (possibly wrapped in `${...}`). Optional `name` attribute.
- **Gateway default flow.** `<exclusiveGateway default="FlowId">` — the parser tags the matching edge `is_default=True` and sets `predicate_expression="default"` if no condition is given.
- **Lanes.** `<laneSet><lane name="..."><flowNodeRef>id</flowNodeRef></lane></laneSet>` — adapter sets `BpmnNodeDef.lane` accordingly.
