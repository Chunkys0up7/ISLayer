# Component 06 — Sequence Runner

## Purpose

Execute a complete journey from start event to terminal state, walking triple-by-triple with an LLM at each step. Detects defects that only emerge across a full sequence: cumulative drift, context bloat, late-journey failures caused by early-journey contract ambiguity.

## Inputs

- `JourneyGraph`.
- A seed context (persona) from component 09.
- Runner configuration: mode, max steps, budget.

## Outputs

- A complete `Trace` (see `contracts/trace-schema.md`).
- `Findings` with `generator=sequence_run`.
- Journey outcome: completed, stuck, regulatory_violation, loop_detected, error.

## Behavior

### B1. Initialize

Set current_node = start event. Initialize JourneyContext from persona. Begin trace.

### B2. Step loop

While current_node is not a terminal event and step count < max_steps:

1. **Check preconditions of current triple against current context.**
   - Evaluate each `ContextAssertion` in `pim.preconditions` using component 04's concrete evaluator.
   - Any unmet precondition emits a finding (class depends on cause: `state_flow_gap` if path absent; `type_mismatch` if present but wrong type) and either halts or proceeds into execution depending on config.
   - Default behavior: proceed into execution and let the LLM's response reveal whether the precondition was actually necessary.

2. **Execute the triple.**
   - Same prompt construction and response parsing as component 05's B1-B2.
   - Capture observed reads and writes.

3. **Apply writes to context.**
   - For each observed write: update context.state, append provenance, detect silent overwrites.
   - Undeclared writes → `output_under_declaration`.
   - Silent overwrites of non-immediate predecessor values → `silent_overwrite`.

4. **Handle obligations.**
   - Append any opened obligations to context.open_obligations.
   - For claimed closures: verify close_conditions are now satisfied; if not → `orphan_obligation` or incomplete closure finding.
   - Check any open obligations whose deadlines have passed → `regulatory_violation`.

5. **Select next node.**
   - For task: follow the single outgoing edge.
   - For exclusive gateway: use LLM's chosen branch (cross-check with static predicate evaluation; disagreement → `branch_misdirection`).
   - For parallel gateway: fork traversal (see B4).

6. **Record step in trace.**

7. **Advance current_node.**

### B3. Termination detection

Journey ends when:
- Reached an end event → outcome = completed.
- Step count exceeds max_steps → outcome = loop_detected, finding `journey_stuck`.
- LLM refuses to proceed and no alternate branch → outcome = stuck, finding depends on refusal reason.
- Regulatory violation detected mid-journey (deadline passed) → outcome = regulatory_violation; may configurably halt or continue for full diagnostic.

### B4. Parallel gateway handling

When encountering a parallel split:
- Fork traversal into separate sub-traces.
- Each sub-trace carries a shared reference to the cumulative context.
- Writes from parallel branches must not conflict — if two branches write the same path, emit `silent_overwrite` finding (parallel-flavored).
- At the converging gateway, merge sub-traces and continue.

For v1, support simple fork-join patterns. Complex multi-instance parallel flows are out of scope and emit a warning.

### B5. Cumulative drift detection

Throughout the journey, monitor:
- **State bloat:** size of context.state grows unboundedly (indicates paths written but never consumed). At end of journey, paths never read by any triple → `context_bloat` candidate (low severity, for SME review).
- **Stale reads:** a triple reads a path that was last written many steps earlier. If the path has since been orthogonally modified (via overwrites or related paths changing), flag as `handoff_implicit_setup` candidate.
- **Contract erosion:** cumulative count of `input_under_declaration` findings across the journey. If late-journey triples have more undeclared reads than early-journey triples, something systemic is happening — emit journey-level `cumulative_drift` finding with detail.

### B6. Regulatory integrity check

At each step:
- Evaluate every open obligation's `must_close_by` condition against current state.
- Deadline past + not closed + not escalated → `regulatory_violation` finding.
- At journey termination: all open obligations not marked `exits_journey: true` → `orphan_obligation` on the opening triple.

### B7. Budget control

Inherit from component 05 — per-step and per-journey token/cost caps. Long journeys on a large corpus can be very expensive; budget is mandatory, not optional.

## Public API

```python
class SequenceRunner:
    def __init__(self, graph: JourneyGraph, llm: LLMClient, evaluator: ExpressionEvaluator, config: RunnerConfig): ...
    def run_journey(self, seed_context: JourneyContext) -> Trace: ...
    def run_many(self, personas: list[Persona]) -> list[Trace]: ...
```

## What this component does NOT do

- Does not generate personas — receives them.
- Does not perform the context isolation test (that is component 07 and operates on trace outputs).
- Does not perform cross-journey analysis — that's component 13 (Report Builder).
- Does not produce final findings aggregated — it emits per-step findings that flow to the finding store.

## Dependencies

- Component 03 (Journey Graph).
- Component 04 (Expression Evaluator — concrete mode).
- Component 09 (Persona Generator).
- LLM client.
- `contracts/journey-context.md`, `contracts/trace-schema.md`.
- Component 12 (Finding Store).

## Verification

**V1.** On a happy-path journey with a clean persona, run_journey completes with outcome=completed, zero findings.

**V2.** On a journey where one triple writes an undeclared path, trace records the observed_writes and emits `output_under_declaration` finding.

**V3.** On a journey where an obligation opens at step 2, deadline at step 5, no close triple: outcome=regulatory_violation at step 5 with corresponding finding.

**V4.** On a journey with a loop and no termination condition: outcome=loop_detected at max_steps, `journey_stuck` finding.

**V5.** On a parallel split where both branches write the same path with different values: `silent_overwrite` finding with parallel flavor.

**V6.** On a clean journey run twice with same seed: traces are structurally identical (step sequence, branch choices).

**V7.** Running with N=5 repeats on a non-deterministic journey produces N traces; aggregation reports modal outcome and variance.

## Implementation notes

- Trace grows large quickly on long journeys; stream trace steps to disk rather than holding in memory.
- Provenance tracking in the context object is the critical infrastructure — instrument carefully.
- For journeys > 30 steps, context size becomes a concern — include a context-size metric in the trace summary.
- When injecting full context into LLM prompts, consider token budget — large contexts late in a journey may force truncation; if truncation occurs, emit `context_bloat` finding even if no other symptom.
- Make the parallel-gateway implementation opt-in behind a feature flag in v1 if it's complex; defer until post-v1 if BPMN doesn't heavily use them.
- Structured output from LLMs: use tool-use / function calling wherever possible to force schema adherence rather than parsing free text.
