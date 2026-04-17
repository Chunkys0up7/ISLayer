# Triple Flow Simulator — Spec Package

Agent-journey simulator for CIM→PIM→PSM triples sourced from bitbucket. Tests the **flow and handoffs between triples**, not the content within them.

## What this tests

Given a corpus of triples (each triple = one BPMN step or decision, realized across CIM intent, PIM executable spec, PSM enriched content), the simulator answers:

1. **Do declared output contracts from triple N actually satisfy declared input contracts of triple N+1?** (Static handoff conformance.)
2. **When executed by a real agent, does triple N's output in practice carry triple N+1 forward, or does triple N+1 silently rely on context outside the declared contract?** (Grounded handoff conformance — the critical test.)
3. **At gateways, does the agent select the correct branch under boundary and ambiguous contexts?** (Decision conformance.)
4. **Across full journeys, does state remain coherent or accumulate drift, overwrites, and stale references?** (Sequence conformance.)
5. **Under volume, edge cases, and complexity injection, which triples fail disproportionately and why?** (Stress diagnostics.)

Every run produces **findings** classified by a formal taxonomy. The output is a ranked defect backlog, not a pass rate.

## What this is NOT

- Not a content validator. The LLM-sourced enrichment is assumed grounded in the corpus; content-level hallucination is a separate concern.
- Not a production runtime. This is a diagnostic harness that runs offline or in CI against triple exports.
- Not a pass/fail gate initially. It is a finding generator. Gating comes after taxonomy is stable and baselines are set.

## Spec package contents

```
specs/
├── 00-master-spec.md              # Overall architecture, project aims, component map
├── contracts/
│   ├── triple-schema.md           # What a triple must expose for simulation
│   ├── journey-context.md         # State object carried through simulation
│   ├── finding-schema.md          # Defect record format and taxonomy
│   └── trace-schema.md            # Per-run execution trace format
├── components/
│   ├── 01-triple-loader.md        # Bitbucket ingestion and parsing
│   ├── 02-triple-inventory.md     # Pre-simulation completeness report
│   ├── 03-journey-graph.md        # BPMN-derived traversable graph
│   ├── 04-static-handoff-checker.md   # Pairwise contract compatibility
│   ├── 05-grounded-handoff-runner.md  # LLM execution of single handoffs
│   ├── 06-sequence-runner.md      # Full-journey execution with per-step capture
│   ├── 07-context-isolation-harness.md # The critical strip-to-declared-contract test
│   ├── 08-branch-boundary-harness.md   # Gateway decision stress
│   ├── 09-persona-generator.md    # Context construction for stress modes
│   ├── 10-perturbation-generator.md    # Field mutation for edge cases
│   ├── 11-finding-classifier.md   # Raw defect → taxonomy tag
│   ├── 12-finding-store.md        # Persistence and query layer for findings
│   └── 13-report-builder.md       # Ranked backlog, heatmaps, trends
└── 99-task-breakdown.md           # Ordered implementation plan for Claude Code
```

## How Claude Code should use this package

1. Read `specs/00-master-spec.md` first to understand the whole system.
2. Read `specs/99-task-breakdown.md` to see the implementation order.
3. For each task, read the referenced component spec and its contract dependencies.
4. Each component spec is self-contained enough to implement in isolation, given the contracts.

## Assumptions baked into this package

- Triples exist in bitbucket and can be exported or cloned locally.
- Each triple can be resolved to a BPMN node ID (task or gateway).
- The BPMN source is available or derivable from the triple set.
- An LLM execution environment (Claude via API or equivalent) is available for grounded modes.
- The enrichment pipeline that sourced corpus content into triples is out of scope for this simulator — its outputs are treated as input.

## Non-goals

- Regenerating or repairing triples. This tool reports; a separate authoring workflow fixes.
- Real-time agent execution. This runs offline against static triple snapshots.
- UI. Reports are file outputs (JSON, markdown, CSV); any UI is downstream.
