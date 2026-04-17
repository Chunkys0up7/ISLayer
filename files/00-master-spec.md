# 00 — Master Spec: Triple Flow Simulator

## 1. Summary

**What:** A diagnostic simulator that walks agent journeys through a corpus of CIM→PIM→PSM triples and produces a classified list of flow and handoff defects.

**Why:** Triples can be individually well-formed (corpus-grounded, LLM-enriched, BPMN-anchored) and still fail to compose into a reliable agentic process because the handoffs between them are under-specified. Current authoring/review processes inspect triples in isolation; this tool inspects the spaces *between* triples.

**Size:** Large. Expected 13 components, implementation in 4 phases.

## 2. Project Context

### Project aim

Validate that a corpus of triples — transformed from a BPMN process and enriched with knowledge articles, regulatory content, and job aids — will support reliable end-to-end agentic execution. Produce a ranked list of defects to drive authoring priorities. Detect when a handoff succeeds only because the executing agent silently supplies context that the declared triple contracts do not guarantee.

### Current state

- Triples exist in bitbucket, one per BPMN step or decision.
- Each triple carries CIM (intent / regulatory references / business rule), PIM (preconditions / postconditions / obligations / decision predicates), and PSM (enriched content: knowledge, regulatory, job aid).
- No systematic testing of inter-triple handoffs exists.
- Defects are discovered ad hoc during downstream development.

### Desired state

- Every triple update triggers a simulator run.
- Every run produces a finding set, classified by the taxonomy defined in `contracts/finding-schema.md`.
- Findings accumulate in a store queryable by triple ID, layer, defect class, and blast radius.
- A ranked backlog report drives the authoring team's weekly priorities.
- Regression detection catches when an authoring change breaks a previously-clean handoff.

### Success criteria

1. On a known-good journey, the simulator runs end-to-end with zero high-severity findings.
2. On a known-broken journey (seeded with representative defects), the simulator detects ≥90% of seeded defects and classifies them correctly under the taxonomy.
3. The context-isolation harness (component 07) identifies at least one handoff that succeeds with full content but fails with declared-only context — the existence of such handoffs proves the diagnostic is working.
4. Report output is directly usable by SMEs without engineering translation.

## 3. Blast Radius Analysis

### Files / systems touched

- Reads from bitbucket (triples) and BPMN source (graph topology).
- Writes finding records to a local store (SQLite or JSONL initially; schema in `contracts/finding-schema.md`).
- Writes trace records per run.
- Writes report artifacts (markdown, JSON, CSV).
- Calls LLM API for grounded modes (Claude via Anthropic API).

### Interfaces affected

- None in production. This is a new, standalone diagnostic tool.

### Downstream dependents

- Authoring team consumes ranked backlog reports.
- CI pipeline (future) consumes pass/fail signals gated on finding counts.
- Enrichment pipeline (separate system) consumes PSM-layer findings as feedback.

### Side effects

- LLM API usage costs scale with grounded-mode coverage. Budget controls required in sequence runner and persona generator.
- Finding store grows monotonically; pruning policy needed.

## 4. Design

### Architecture

Five logical layers, implemented as 13 components:

```
┌─────────────────────────────────────────────────────────┐
│  INGESTION LAYER                                        │
│  [01 Triple Loader] → [02 Triple Inventory]             │
│                                                         │
│  Produces: validated triple set + completeness report   │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│  GRAPH LAYER                                            │
│  [03 Journey Graph]                                     │
│                                                         │
│  Produces: traversable BPMN graph with triple bindings  │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│  SIMULATION LAYER                                       │
│  [04 Static Handoff Checker]  ← runs on graph alone     │
│  [05 Grounded Handoff Runner] ← one pair, LLM executes  │
│  [06 Sequence Runner]         ← full journey, LLM       │
│  [07 Context Isolation]       ← critical diagnostic     │
│  [08 Branch Boundary]         ← gateway stress          │
│                                                         │
│  Inputs: graph + contexts from generators               │
│  Outputs: traces + raw findings                         │
└─────────────────────────────────────────────────────────┘
                         ↑
┌─────────────────────────────────────────────────────────┐
│  GENERATION LAYER                                       │
│  [09 Persona Generator]                                 │
│  [10 Perturbation Generator]                            │
│                                                         │
│  Produces: seed contexts for simulation                 │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  ANALYSIS LAYER                                         │
│  [11 Finding Classifier] → [12 Finding Store] → [13 Report] │
│                                                         │
│  Produces: ranked backlog, heatmaps, trends             │
└─────────────────────────────────────────────────────────┘
```

### Key design decisions

**D1: Simulation runs against the declared contracts first, then against the enriched content.** This is deliberate. The whole architectural bet is that the contracts, not the content, are what compose. Component 07 (Context Isolation Harness) is the instrument that proves or falsifies this bet for each handoff. If skipped, the simulator becomes an expensive content review tool.

**D2: Findings are classified by an explicit taxonomy, not free-text.** See `contracts/finding-schema.md`. Raw simulator output is unclassified; a dedicated classifier component (11) tags findings against the taxonomy. This separation allows the taxonomy to evolve without touching simulation logic.

**D3: Static checks run on every triple update; grounded checks run on a schedule or on-demand.** Static is cheap and deterministic. Grounded is expensive and stochastic. The tiering is how this tool stays fast enough to be run routinely.

**D4: Traces are first-class artifacts, not ephemeral logs.** Every run produces a trace file (schema in `contracts/trace-schema.md`). Traces are diffable; finding regressions are detected by trace diff.

**D5: No triple repair inside the simulator.** The simulator reports. A separate authoring workflow fixes. This keeps the simulator simple and prevents the anti-pattern where the tool silently papers over defects it should be surfacing.

**D6: Generators are deterministic given a seed.** Persona generation, perturbation, and adversarial context construction all take a seed parameter. Reproducibility is required for regression detection.

**D7: Component boundaries follow the data flow, not the code organization.** Each component has one clearly-defined input and one clearly-defined output (specified in its individual spec). This makes the system parallelizable for implementation and testable at the boundaries.

### Alternatives considered

**A1: Single monolithic simulator.** Rejected. The logical phases (ingestion, graph, simulation, generation, analysis) evolve on different cadences and benefit from independent testing. Monolithic designs entangle concerns and make the context-isolation test impossible to isolate cleanly.

**A2: Run simulation only in grounded mode, skip static checks.** Rejected. Static checks catch 40-60% of defects at near-zero cost; running grounded-only wastes LLM budget on defects static would have found instantly.

**A3: Generate findings directly from traces without a classifier step.** Rejected. Classification discipline requires the separation — otherwise the taxonomy becomes whatever the simulator happened to emit, rather than what the authoring team needs to act on.

**A4: Treat BPMN as input to the simulator instead of deriving graph from triples.** Not exactly rejected — see component 03 for how both paths are supported. The triples carry their BPMN anchor; the graph is reconstructed from that. If the BPMN source is available directly, it's used for cross-validation.

### Constraints and assumptions

**C1:** Triples are readable from bitbucket without requiring live access during simulation — export once, run many.

**C2:** Each triple declares (or can have extracted) an input contract and output contract. If a triple lacks these, that is itself a finding produced by component 02 (Inventory), and the triple is excluded from downstream simulation.

**C3:** The LLM used for grounded modes is deterministic enough at temperature 0 with a fixed seed to produce reproducible traces. N=5 repeats for stochastic behavior are captured in the trace.

**C4:** Journey state can be represented as a typed, append-mostly object with explicit provenance pointers. Event-sourced state with projections is out of scope for v1 but the schema leaves room for migration.

**C5:** The simulator does not execute real downstream systems — tool calls are mocked or stubbed at the PSM boundary. This is a diagnostic, not an integration test.

## 5. Task Breakdown

See `99-task-breakdown.md` for the full ordered implementation plan.

Summary of phases:
- **Phase 1 — Foundation (components 01, 02, 03):** ingest and structure triples, produce the inventory report. Delivers value immediately without any simulation.
- **Phase 2 — Static simulation (component 04):** pairwise handoff conformance. First real flow findings.
- **Phase 3 — Grounded simulation (components 05, 06, 07, 08):** LLM-backed execution. Component 07 is the highest-leverage test in the whole system and must be built early in this phase.
- **Phase 4 — Generators and analysis (components 09, 10, 11, 12, 13):** stress testing, classification, reporting.

## 6. Risks and Mitigations

**R1: Triples lack explicit input/output contracts.**
*Likelihood:* High. *Impact:* High.
*Mitigation:* Component 02 produces a contract-completeness report as its primary output. Triples without contracts are flagged, not simulated. The simulator's first value delivery is this report, which justifies the authoring work to add contracts.

**R2: LLM non-determinism produces noisy findings in grounded modes.**
*Likelihood:* Medium. *Impact:* Medium.
*Mitigation:* N=5 repeats per grounded test, findings report modal outcome and variance. Low-variance consistent failures are high-confidence; high-variance behavior is a finding in itself (interface ambiguity).

**R3: Finding volume overwhelms the authoring team.**
*Likelihood:* High on first full run. *Impact:* Medium.
*Mitigation:* Report builder (13) ranks by severity × blast radius, caps the default backlog at top 20, and exposes filtered views. First run is expected to produce hundreds of findings; triage is a one-time cost.

**R4: Context isolation harness (07) produces too many "relies on external context" findings, making it useless.**
*Likelihood:* Medium. *Impact:* High — this is the keystone diagnostic.
*Mitigation:* Calibrate by running 07 against a set of handoffs SMEs have manually verified. If false positive rate is high, the harness needs the triple content to be decomposed more carefully. This is the one component that needs SME calibration before it ships.

**R5: Generators produce unrealistic contexts that surface non-defects.**
*Likelihood:* Medium. *Impact:* Low-medium.
*Mitigation:* Personas are seeded from real historical cases where possible. Perturbation mutations are constrained to values that could plausibly occur. Review process catches unrealistic-context findings and adjusts generators.

**R6: Taxonomy drift — classifier tags become inconsistent over time.**
*Likelihood:* Medium over months. *Impact:* Medium.
*Mitigation:* Classifier (11) is specified as a separate component with its own tests. Taxonomy version is recorded in every finding. Changes to taxonomy require migration of existing findings.

## 7. Verification Plan

### Integration check

Run the full pipeline end-to-end on a test corpus (5-10 triples representing one simple journey, known-good). Expected outcome:
- Component 01 loads all triples.
- Component 02 reports 100% contract completeness.
- Component 03 produces a connected graph.
- Component 04 reports zero handoff defects.
- Component 06 sequence-runs the journey to terminal success.
- Component 07 produces zero isolation failures.
- Component 13 produces an empty ranked backlog.

### Regression check

Seed the test corpus with one defect of each taxonomy class. Re-run. Expected outcome: every seeded defect appears in the ranked backlog with correct classification.

### Acceptance criteria

- All 13 components have their specified inputs and outputs.
- End-to-end run completes in bounded time (target: < 10 minutes for 100-triple corpus in static mode; grounded mode is budget-bounded by persona count).
- Findings are reproducible given the same triple snapshot and generator seeds.
- Report output is reviewable by a SME without engineering intervention.
