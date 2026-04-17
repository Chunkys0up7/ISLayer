# Contract: Triple Schema

This contract defines the minimum structure a triple must expose to be simulated. Triples in bitbucket may carry additional fields; this contract specifies what the simulator *requires*.

## Required fields

### Identity

| Field | Type | Purpose |
|-------|------|---------|
| `triple_id` | string (stable, unique) | Primary key. Used in findings, traces, and cross-references. |
| `version` | string (semver or hash) | Required for trace reproducibility. |
| `bpmn_node_id` | string | The BPMN task or gateway this triple realizes. Anchors the triple in the journey graph. |
| `bpmn_node_type` | enum: `task`, `exclusive_gateway`, `parallel_gateway`, `start_event`, `end_event`, `intermediate_event` | Governs which contract rules apply. |

### CIM layer

| Field | Type | Purpose |
|-------|------|---------|
| `cim.intent` | string | Business-level statement of what this step accomplishes. One sentence. |
| `cim.regulatory_refs` | list of `{citation, rule_text, obligation_type}` | Regulatory rules bound to this step. `obligation_type` ∈ `{opens, closes, enforces, references}`. |
| `cim.business_rules` | list of `{rule_id, rule_text, evaluable_form?}` | Business rules governing this step. `evaluable_form` is optional but required for gateways. |

### PIM layer

| Field | Type | Purpose |
|-------|------|---------|
| `pim.preconditions` | list of `ContextAssertion` | What must be in journey context on entry. See ContextAssertion below. |
| `pim.postconditions` | list of `ContextAssertion` | What will be in journey context on exit. |
| `pim.obligations_opened` | list of `ObligationSpec` | Regulatory/timing commitments this step creates. |
| `pim.obligations_closed` | list of `obligation_id` | Obligations this step resolves. |
| `pim.decision_predicates` | list of `BranchPredicate` | **Required for gateway nodes.** Null for task nodes. |
| `pim.state_writes` | list of `StateFieldRef` | Journey state fields this step writes. |
| `pim.state_reads` | list of `StateFieldRef` | Journey state fields this step reads. |

### PSM layer

| Field | Type | Purpose |
|-------|------|---------|
| `psm.enriched_content` | list of `ContentChunk` | The LLM-sourced corpus content bound to this step. |
| `psm.prompt_scaffold` | string or template ref | Any prompt structure wrapping the content when handed to the agent. |
| `psm.tool_bindings` | list of `ToolRef` | Tools (real or mocked) this step may invoke. |

## Subtype definitions

### `ContextAssertion`

```
{
  path: string,                    # Dotted path into journey state, e.g. "borrower.income.verified"
  predicate: string,               # One of: exists, equals, in_range, matches_pattern, satisfies_expression
  value?: any,                     # Operand for the predicate
  type: string,                    # Expected type: boolean, string, number, timestamp, enum, object
  source_triple?: string           # For preconditions: which upstream triple is expected to produce this
}
```

### `ObligationSpec`

```
{
  obligation_id: string,
  description: string,
  regulatory_ref?: string,         # Cross-reference to cim.regulatory_refs
  must_close_by?: {                # Optional timing constraint
    condition: string,             # e.g. "within_business_days(3, anchor=application_received_at)"
    anchor: StateFieldRef
  },
  close_conditions: list of ContextAssertion   # What must be true for this obligation to be considered closed
}
```

### `BranchPredicate`

```
{
  edge_id: string,                 # The outgoing BPMN edge this predicate governs
  predicate_expression: string,    # Evaluable expression over journey state
  evidence_refs: list of string,   # Triple content or regulatory refs that justify this predicate
  is_default: boolean              # True if this is the fallback branch
}
```

Exclusive gateways must have predicates whose evaluations partition the context space: exactly one branch true for any given context.

### `StateFieldRef`

```
{
  path: string,                    # Dotted path, e.g. "loan.le.sent_at"
  type: string,                    # Expected type
  namespace?: string               # Optional grouping, e.g. "borrower", "loan", "regulatory"
}
```

### `ContentChunk`

```
{
  chunk_id: string,
  source_document: string,         # URI or ID of the corpus document
  content_type: enum: knowledge, regulatory, job_aid,
  text: string,
  retrieval_metadata?: {           # Provenance from the LLM enrichment
    retrieved_at: timestamp,
    retrieval_confidence?: number,
    source_span?: {start, end}
  }
}
```

### `ToolRef`

```
{
  tool_id: string,
  purpose: string,
  mock_response_template?: string  # For simulation: what the tool would return
}
```

## Required invariants

These invariants are checked by component 02 (Triple Inventory) and failures are emitted as findings, not exceptions.

**I1 — Identity completeness.** Every triple has `triple_id`, `version`, `bpmn_node_id`, `bpmn_node_type`.

**I2 — Layer presence.** Every triple has `cim`, `pim`, and `psm` objects. Missing layers are finding class `layer_missing` at the layer of the missing object.

**I3 — Intent statement.** `cim.intent` is non-empty and is a single sentence.

**I4 — Contract declaration.** `pim.preconditions`, `pim.postconditions`, `pim.state_reads`, `pim.state_writes` are all present (may be empty lists, but must exist as fields).

**I5 — Gateway predicates.** If `bpmn_node_type` is `exclusive_gateway` or `parallel_gateway`, `pim.decision_predicates` is non-empty. Missing → finding class `evaluability_gap` at PIM.

**I6 — Obligation closure tracking.** Every `obligation_id` listed in `pim.obligations_opened` anywhere in the corpus must appear in at least one `pim.obligations_closed` list, OR be explicitly marked as `exits_journey: true` on the opening triple.

**I7 — State-flow referential integrity.** Every `path` in `pim.preconditions` and `pim.state_reads` must appear in `pim.state_writes` or `pim.postconditions` of some other triple reachable upstream in the graph. Orphan reads → finding class `state_flow_gap` at PIM.

**I8 — Content presence.** `psm.enriched_content` is non-empty for task and gateway nodes. Events may have empty content.

**I9 — Predicate evaluability.** `predicate_expression` in `BranchPredicate` must be parseable by the simulator's expression evaluator (see component 04 for evaluator spec). Unparseable → finding class `evaluability_gap` at PIM.

**I10 — Regulatory resolution.** Every `regulatory_ref` in an obligation resolves to an entry in `cim.regulatory_refs`.

## Handling missing or malformed triples

- Triples failing I1 (identity completeness) are **excluded** from simulation entirely. Listed in inventory report.
- Triples failing I2–I4 (layer/contract presence) are **included** in inventory report but **excluded** from downstream simulation until fixed.
- Triples failing I5–I10 are **included** in simulation; the violations themselves are emitted as findings so they appear in the backlog.

## Extraction note

If existing triples in bitbucket do not carry this schema explicitly, component 01 (Triple Loader) is responsible for extracting or deriving the fields. Where derivation is impossible (e.g., no preconditions authored), component 02 (Inventory) reports the gap. **The simulator does not fabricate contracts.** Missing contracts are findings, not silently filled defaults.
