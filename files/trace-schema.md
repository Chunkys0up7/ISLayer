# Contract: Trace Schema

A trace is a first-class artifact produced by every simulator run. Traces are diffable, reproducible given inputs, and form the evidence base for all findings.

## Trace record

```
Trace {
  trace_id: string,                # UUID
  run_id: string,                  # Groups traces from a single simulator invocation
  created_at: timestamp,

  # Reproducibility envelope
  simulator_version: string,
  taxonomy_version: string,
  corpus_version: string,          # Hash of triple set
  bpmn_version: string,            # Hash of BPMN source
  generator_config: {
    persona_seed: int,
    perturbation_seed?: int,
    mode: enum: static | grounded | isolated | branch_boundary | perturbation | ablation
  },
  llm_config?: {                   # Only for grounded modes
    model: string,
    model_version: string,
    temperature: number,
    seed: int,
    prompt_template_version: string
  },

  # Inputs
  seed_context: JourneyContext,    # The starting state
  persona: Persona,

  # Execution
  steps: list of TraceStep,

  # Outcome
  outcome: enum: completed | stuck | regulatory_violation | loop_detected | error,
  outcome_node: string,            # The node where outcome was determined
  final_context: JourneyContext,

  # Summary metrics (computed)
  metrics: {
    steps_executed: int,
    duration_ms: int,
    total_tokens_in?: int,
    total_tokens_out?: int,
    findings_count_by_class: dict,
    obligations_opened: int,
    obligations_closed: int,
    obligations_unclosed: int
  },

  # Findings emitted during this trace
  finding_ids: list of string
}
```

## `TraceStep`

One entry per triple execution.

```
TraceStep {
  step_index: int,
  triple_id: string,
  triple_version: string,
  bpmn_node_id: string,
  bpmn_node_type: string,

  entered_at: timestamp,
  exited_at: timestamp,
  duration_ms: int,

  # State transitions
  state_hash_in: string,           # Hash of JourneyContext.state on entry
  state_hash_out: string,
  state_diff: StateDiff,           # What changed

  # Contract observation
  declared_reads: list of StateFieldRef,
  observed_reads: list of StateFieldRef,
  declared_writes: list of StateFieldRef,
  observed_writes: list of StateFieldRef,

  # Execution mode specific
  static_evaluation?: StaticResult,
  llm_interaction?: LLMInteractionRecord,
  isolation_comparison?: IsolationResult,

  # Gateway specific
  branch_evaluation?: {
    predicates_evaluated: list of {edge_id, expression, result, evidence},
    branch_taken: string,
    branch_agreed_between_static_and_grounded?: boolean
  },

  # Findings attributed to this step
  findings: list of finding_id
}
```

## `StateDiff`

```
{
  added: dict,                     # Paths newly written
  modified: dict,                  # Paths changed, with {old_value, new_value}
  unchanged_but_read: list of string
}
```

## `StaticResult`

For static mode execution, records what the checker decided.

```
{
  preconditions_satisfied: list of {assertion, result: true|false, evaluator_note},
  postconditions_declared: list of ContextAssertion,
  obligations_opened: list of obligation_id,
  obligations_closed: list of obligation_id,
  passed: boolean,
  failure_reasons: list of string
}
```

## `IsolationResult`

The core output of component 07 — compares full-content execution vs. declared-contract-only execution.

```
{
  full_content_outcome: enum: success | partial | failure,
  declared_only_outcome: enum: success | partial | failure,
  divergence: boolean,             # True if outcomes differ
  divergence_signature: {          # Populated only if divergence=true
    missing_without_content: list of StateFieldRef,   # What was produced with content but not without
    extra_with_content: list of StateFieldRef,        # What content provided that declarations did not
    behavior_change: string                             # Natural-language description of the difference
  }
}
```

An `IsolationResult.divergence == true` is the strongest signal the simulator produces. It means this handoff relies on content outside the declared contract — a `handoff_carried_by_external_context` finding.

## Trace storage

- Traces serialize to JSON.
- One trace per (triple-run) × (persona) × (mode) combination.
- Storage layout: `traces/<run_id>/<trace_id>.json`.
- Compressed after run completion (gzip).
- Retention: configurable; default 90 days. Traces referenced by unresolved findings are preserved regardless.

## Trace diff

Component 13 (Report Builder) computes trace diffs to detect regressions:

```
TraceDiff {
  trace_a: trace_id,
  trace_b: trace_id,
  corpus_version_a: string,
  corpus_version_b: string,

  outcome_changed: boolean,
  new_findings: list of finding_id,       # In b but not a
  resolved_findings: list of finding_id,  # In a but not b
  persistent_findings: list of finding_id,

  state_divergence_first_at_step: int | null,
  state_divergence_detail?: StateDiff
}
```

Trace diffs are the mechanism by which authoring changes are validated: a corpus update should produce either no trace diff (if unrelated journeys) or a diff with only the intended resolved findings and no new ones.

## Reproducibility requirements

Given identical:
- `corpus_version`
- `bpmn_version`
- `persona`
- `generator_config.persona_seed` and `perturbation_seed`
- `llm_config` (including seed)

…re-running must produce identical traces in static and isolated modes, and must produce traces with identical structure (same steps, same branch decisions) in grounded mode across N=5 repeats with the pinned seed. Structural differences across repeats are themselves traced and emit a `nondeterminism` observation (not a finding, but a diagnostic note).
