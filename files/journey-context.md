# Contract: Journey Context

The journey context is the mutable state object carried through a simulation. Every triple reads from it and writes to it. Its design is critical because handoff defects are, fundamentally, context defects.

## Structure

```
JourneyContext {
  journey_id: string,              # UUID per simulation run
  persona_id: string,              # Which persona seeded this journey
  started_at: timestamp,
  current_node: string,            # BPMN node ID
  corpus_version: string,          # Hash of triple set
  journey_spec_version: string,    # Hash of BPMN + persona config

  state: StateObject,              # The domain-specific state (see below)
  provenance: ProvenanceLog,
  history: list of NodeExecution,
  open_obligations: list of OpenObligation,
  closed_obligations: list of ClosedObligation,
  attestations: list of Attestation
}
```

## `StateObject`

Namespaced fields written by triples via `pim.state_writes` and read via `pim.state_reads`. Represented as a nested dict with string keys and typed values.

```
{
  borrower: {
    identity: { verified: bool, method: string, verified_at: timestamp },
    income: { source: enum, amount: number, verified: bool },
    application: { received_at: timestamp, six_elements_complete: bool }
  },
  loan: {
    product: string,
    terms: { rate: number, apr: number, amount: number },
    le: { sent_at: timestamp, version: int, delivery_method: string }
  },
  ...
}
```

Namespaces are not fixed — they emerge from the triples' `state_writes`. The simulator treats state as schema-on-write: the first triple to write a path establishes its type, and subsequent writes must conform (or a finding is emitted).

## `ProvenanceLog`

For every field in state, records which triple wrote it and when.

```
provenance: {
  "<dotted_path>": [
    {
      written_by_triple: string,
      written_at_step: int,         # Index into history
      value_hash: string,            # For detecting silent overwrites
      derived_from: list of string  # chunk_ids from psm.enriched_content, if applicable
    }
  ]
}
```

A state path with multiple provenance entries means it has been overwritten. This is the detection mechanism for the `silent_overwrite` finding class.

## `NodeExecution`

One entry per triple executed during the journey.

```
{
  step_index: int,
  triple_id: string,
  bpmn_node_id: string,
  entered_at_state_hash: string,   # Hash of state on entry
  exited_at_state_hash: string,    # Hash of state on exit
  mode: enum: static, grounded, isolated,
  duration_ms: int,
  state_reads_observed: list of StateFieldRef,
  state_writes_observed: list of StateFieldRef,
  obligations_opened: list of obligation_id,
  obligations_closed: list of obligation_id,
  branch_taken?: edge_id,          # For gateway nodes
  branch_evidence?: list of chunk_id,
  llm_interaction?: LLMInteractionRecord,   # Only in grounded/isolated modes
  findings_emitted: list of finding_id
}
```

## `LLMInteractionRecord`

When an LLM executes a triple, this captures enough to reproduce and audit the interaction.

```
{
  model: string,
  model_version: string,
  temperature: number,
  seed: int,
  prompt_template_version: string,
  prompt_sent: string,              # Full prompt
  content_provided: list of chunk_id,
  context_provided: dict,           # Subset of state handed to LLM
  raw_response: string,
  parsed_response: dict,
  token_counts: {input, output},
  refusals: list of {type, reason}  # If the model declined to proceed
}
```

## `OpenObligation`

```
{
  obligation_id: string,
  opened_at_step: int,
  opened_by_triple: string,
  must_close_by?: {
    deadline: timestamp | null,    # Null if not time-bound
    anchor_state_path: string
  },
  close_conditions: list of ContextAssertion
}
```

## Mutation discipline

The journey context has strict rules enforced by the sequence runner (component 06):

**M1 — State writes require declaration.** A triple can only write paths declared in its `pim.state_writes`. Undeclared writes are detected and emitted as finding class `output_under_declaration`.

**M2 — State reads require declaration.** A triple can only read paths declared in its `pim.state_reads`. Undeclared reads are the core signal for the context isolation harness (component 07).

**M3 — Type conformance.** Once a path has an established type, subsequent writes must match. Mismatches emit finding class `type_mismatch`.

**M4 — Provenance is append-only.** Each write appends to the path's provenance list. Detecting repeated provenance entries is how `silent_overwrite` findings are generated.

**M5 — Obligation lifecycle.** Opened obligations must be closed before journey termination, OR the terminating triple must mark them `exits_journey: true`. Unclosed obligations at terminal state emit finding class `orphan_obligation`.

## Context snapshots

For debugging and regression comparison, the sequence runner emits context snapshots at configurable points:
- Always: entry and exit of every triple (hashed only, for trace compactness).
- Optionally: full JSON snapshot at configurable step indices.
- Always: full JSON snapshot on any finding emission.

## Serialization

JourneyContext serializes to JSON. Trace schema (see `trace-schema.md`) includes a sequence of JourneyContext states. Comparing two contexts by their state_hash detects divergence in regression runs.
