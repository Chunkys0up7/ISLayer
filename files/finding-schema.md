# Contract: Finding Schema and Taxonomy

A finding is a single defect record. Every simulator output that describes "something wrong" is a finding conforming to this schema. The taxonomy is the controlled vocabulary used to classify findings.

## Finding record

```
Finding {
  finding_id: string,              # UUID, stable per detection
  detected_at: timestamp,
  taxonomy_version: string,

  # Classification (required)
  layer: enum: CIM | PIM | PSM,
  defect_class: enum,              # See taxonomy below
  generator: enum,                 # What surfaced it
  severity: enum: regulatory | correctness | efficiency | cosmetic,
  confidence: enum: high | medium | low,

  # Attribution (required)
  primary_triple_id: string,
  related_triple_ids: list of string,   # For handoff defects, typically [producer, consumer]
  bpmn_node_id: string,
  bpmn_edge_id?: string,           # For handoff findings

  # Evidence (required)
  summary: string,                 # One-sentence description
  detail: string,                  # Longer explanation
  evidence: {
    journey_id?: string,
    step_index?: int,
    observed: any,                 # What the simulator saw
    expected: any,                 # What the contract required
    trace_ref: string              # Pointer into trace file
  },

  # Blast radius (computed by finding store on insertion)
  journeys_affected_count: int,
  journeys_affected_pct: number,
  is_on_critical_path: boolean,

  # State (lifecycle)
  status: enum: new | triaged | accepted | suppressed | fixed | regressed,
  suppression_reason?: string,
  first_seen_run: string,
  last_seen_run: string,
  occurrence_count: int
}
```

## Taxonomy — `defect_class` enum

The core controlled vocabulary. Every finding must map to exactly one. Adding a new class requires a taxonomy version bump and migration.

### Structure defects (typically detected in static modes)

| Class | Layer | Description |
|-------|-------|-------------|
| `layer_missing` | Any | A required MDA layer is absent from the triple. |
| `identity_incomplete` | N/A | Triple is missing one or more of triple_id, version, bpmn_node_id, bpmn_node_type. |
| `orphan_triple` | PIM | Triple is not reachable from any start event in the journey graph. |
| `orphan_obligation` | PIM | Obligation opened but never closed on at least one terminal path. |
| `regulatory_orphan` | CIM | Regulatory reference in obligation does not resolve to declared regulatory_refs. |

### Contract defects (detected in static and grounded modes)

| Class | Layer | Description |
|-------|-------|-------------|
| `contract_missing` | PIM | Triple lacks preconditions, postconditions, state_reads, or state_writes fields entirely. |
| `output_under_declaration` | PIM | Observed writes during execution include paths not declared in state_writes. |
| `output_over_promise` | PIM | Declared postcondition or state_write did not occur in a grounded execution. |
| `input_under_declaration` | PIM | Observed reads during execution include paths not declared in state_reads. Key signal for context-isolation findings. |
| `type_mismatch` | PIM | Producer writes path with type X; consumer expects type Y. |
| `state_flow_gap` | PIM | Consumer reads path that no upstream triple writes. |
| `silent_overwrite` | PIM | Triple writes a path previously written by a non-immediate predecessor, potentially losing data. |

### Decision defects

| Class | Layer | Description |
|-------|-------|-------------|
| `evaluability_gap` | PIM | Gateway decision expressed in prose, not as evaluable predicate. |
| `predicate_non_partitioning` | PIM | Gateway predicates do not partition context space (overlap or gap). |
| `branch_misdirection` | PSM | Agent selected a branch inconsistent with evaluated predicate. |
| `escalation_failure` | PSM | Context was ambiguous; agent proceeded without escalating. |

### Content defects (typically PSM layer)

| Class | Layer | Description |
|-------|-------|-------------|
| `content_missing` | PSM | Step requires content for a concept referenced in its intent; no matching content in enriched chunks. |
| `content_stale` | PSM | Content references a regulation, policy, or version that is outdated per cim.regulatory_refs. |
| `content_adjacent_not_actionable` | PSM | Content describes the domain but does not contain the specific information needed to execute the step. |
| `content_contradicts` | PSM | Two content chunks in the same triple contain conflicting information. |

### Handoff defects (the core of this simulator's value)

| Class | Layer | Description |
|-------|-------|-------------|
| `handoff_carried_by_external_context` | PIM | Grounded execution succeeds with full content but fails under context isolation — handoff relied on content outside declared contracts. **This is the most valuable finding class.** |
| `handoff_format_mismatch` | PIM | Producer and consumer agree on field name but disagree on format/granularity. |
| `handoff_implicit_setup` | PIM | Consumer depends on state that is "obviously" true but not written by any triple. |
| `handoff_naming_drift` | PIM | Producer writes `field_a`; consumer reads `field_a_value` — semantically same but syntactically divergent. |

### Journey-level defects

| Class | Layer | Description |
|-------|-------|-------------|
| `cumulative_drift` | PIM | State at step N subtly wrong; no individual handoff failed but terminal output is incorrect. |
| `context_bloat` | PSM | Accumulated state exceeds effective processing window; later steps ignore earlier-set fields. |
| `journey_stuck` | Any | Journey cannot progress from a node despite preconditions appearing satisfied. |
| `regulatory_violation` | CIM | Completed journey violates a declared regulatory obligation. |

## Taxonomy — `generator` enum

Tracks which simulator mode surfaced the finding. Drives diagnosis of simulator coverage.

| Generator | Description |
|-----------|-------------|
| `inventory` | Pre-simulation static analysis (component 02). |
| `static_handoff` | Component 04 — contract compatibility checks. |
| `grounded_pair` | Component 05 — single handoff LLM execution. |
| `sequence_run` | Component 06 — full journey LLM execution. |
| `context_isolation` | Component 07 — the strip-to-declared-contract diagnostic. |
| `branch_boundary` | Component 08 — gateway stress. |
| `perturbation` | Component 10 — field mutation. |
| `ablation` | Component 10 — triple/content removal. |
| `volume` | Component 06 at scale — statistical failure concentration. |

## Taxonomy — `severity` enum

| Severity | Criterion |
|----------|-----------|
| `regulatory` | If this defect reached production, it would cause or enable a regulatory compliance violation. |
| `correctness` | If this defect reached production, the agent would produce wrong output or take wrong action in this step. |
| `efficiency` | Agent completes correctly but the process is suboptimal (redundant retrieval, unnecessary escalation, etc.). |
| `cosmetic` | Authoring quality issue with no execution impact. |

Severity is assigned by the finding classifier (component 11) based on rules that reference the defect class, the affected regulatory obligations, and the layer.

## Taxonomy — `confidence` enum

| Confidence | Criterion |
|------------|-----------|
| `high` | Static/symbolic detection, deterministic. OR: grounded detection consistent across all N repeat runs. |
| `medium` | Grounded detection inconsistent but > 50% of repeat runs. |
| `low` | Grounded detection in < 50% of repeat runs, OR first-time observation needing calibration. |

Low-confidence findings are included in the store but excluded from default backlog reports.

## Blast radius calculation

Computed by finding store (component 12) on insertion and updated nightly:

- `journeys_affected_count` — number of distinct journey_ids that have this finding.
- `journeys_affected_pct` — count divided by total journeys in the run set.
- `is_on_critical_path` — true if the affected triple sits on the BPMN happy-path as marked in the journey graph metadata.

## Lifecycle states

- `new` — first detection.
- `triaged` — SME has reviewed and acknowledged; next action assigned.
- `accepted` — acknowledged but deferred (with reason); not fixed yet.
- `suppressed` — marked as false positive or deliberately-accepted behavior; excluded from reports (with reason recorded).
- `fixed` — authoring change made; not seen in latest run.
- `regressed` — previously `fixed`, reappeared in a later run.

Transitions between states are recorded as events for trend analysis.
