# Component 12 — Finding Store

## Purpose

Persistent, queryable storage for all findings. Computes blast radius. Tracks lifecycle state. Enables trend analysis and regression detection across runs.

## Inputs

- `Finding` records from component 11 (Classifier).
- `Trace` records from simulation components (04-08, 10).
- Query requests from component 13 (Report Builder) and external consumers.

## Outputs

- Persisted findings with computed blast radius and lifecycle state.
- Query results in structured form.
- Change events (new, regressed, resolved) for subscribers.

## Behavior

### B1. Storage backend

v1 implementation: SQLite.
- Schema: findings, traces, runs, suppressions, transitions, detections.
- File-based, no server required, portable.
- Suitable for corpus sizes up to ~10,000 triples and millions of findings.

Future: Postgres for multi-user teams, queryable dashboards.

### B2. Schema

```sql
CREATE TABLE runs (
  run_id TEXT PRIMARY KEY,
  started_at TIMESTAMP,
  completed_at TIMESTAMP,
  corpus_version TEXT,
  bpmn_version TEXT,
  simulator_version TEXT,
  taxonomy_version TEXT,
  config_json TEXT
);

CREATE TABLE findings (
  finding_id TEXT PRIMARY KEY,
  first_seen_run TEXT REFERENCES runs(run_id),
  last_seen_run TEXT REFERENCES runs(run_id),
  taxonomy_version TEXT,
  layer TEXT,
  defect_class TEXT,
  generator TEXT,
  severity TEXT,
  severity_override TEXT,
  confidence TEXT,
  primary_triple_id TEXT,
  bpmn_node_id TEXT,
  bpmn_edge_id TEXT,
  summary TEXT,
  detail TEXT,
  evidence_json TEXT,
  status TEXT,
  occurrence_count INTEGER,
  regression_count INTEGER,
  created_at TIMESTAMP,
  updated_at TIMESTAMP
);

CREATE INDEX idx_findings_triple ON findings(primary_triple_id);
CREATE INDEX idx_findings_class ON findings(defect_class);
CREATE INDEX idx_findings_status ON findings(status);
CREATE INDEX idx_findings_run ON findings(last_seen_run);

CREATE TABLE finding_related_triples (
  finding_id TEXT REFERENCES findings(finding_id),
  related_triple_id TEXT,
  PRIMARY KEY (finding_id, related_triple_id)
);

CREATE TABLE traces (
  trace_id TEXT PRIMARY KEY,
  run_id TEXT REFERENCES runs(run_id),
  persona_id TEXT,
  mode TEXT,
  outcome TEXT,
  trace_file_path TEXT,
  created_at TIMESTAMP
);

CREATE TABLE finding_traces (
  finding_id TEXT REFERENCES findings(finding_id),
  trace_id TEXT REFERENCES traces(trace_id),
  step_index INTEGER,
  PRIMARY KEY (finding_id, trace_id, step_index)
);

CREATE TABLE transitions (
  transition_id TEXT PRIMARY KEY,
  finding_id TEXT REFERENCES findings(finding_id),
  from_status TEXT,
  to_status TEXT,
  actor TEXT,
  reason TEXT,
  transitioned_at TIMESTAMP
);

CREATE TABLE suppressions (
  finding_id TEXT PRIMARY KEY REFERENCES findings(finding_id),
  reason TEXT,
  suppressed_by TEXT,
  suppressed_at TIMESTAMP,
  expires_at TIMESTAMP
);

CREATE TABLE blast_radius (
  finding_id TEXT PRIMARY KEY REFERENCES findings(finding_id),
  journeys_affected_count INTEGER,
  journeys_affected_pct REAL,
  is_on_critical_path BOOLEAN,
  computed_at_run TEXT REFERENCES runs(run_id)
);
```

### B3. Ingestion

On `emit_finding(finding)`:
1. Check for existing finding with matching (`defect_class`, `primary_triple_id`, `related_triple_ids`, `taxonomy_version`).
2. If match:
   - Update `last_seen_run`.
   - Increment `occurrence_count`.
   - If `status == 'fixed'` → transition to `regressed`, increment `regression_count`, record transition.
   - Update confidence and evidence if improved.
3. If no match:
   - Insert new finding with `status='new'`, `occurrence_count=1`.
   - Record initial transition `null → new`.

### B4. Blast radius computation

On run completion (not per finding — batched at run end):

For each finding:
- Count distinct trace_ids referencing this finding → `journeys_affected_count`.
- Divide by total traces in the run → `journeys_affected_pct`.
- Check if `bpmn_node_id` is on the critical path (per graph metadata) → `is_on_critical_path`.
- Write row to `blast_radius` for this run.

Historical blast radius persists per run, enabling trend analysis.

### B5. Detecting resolved findings

After a run completes, for each finding with `status ∈ {new, triaged, accepted, regressed}`:
- Check if it appeared in the most recent run.
- If not seen in the most recent run AND the corpus_version changed → transition to `fixed`, record transition.
- If not seen in the most recent run AND the corpus_version did NOT change → leave as-is (absence may be stochastic).

### B6. Query API

Common queries needed by component 13:

- `get_findings(filters)` — filter by layer, defect_class, severity, status, generator, triple_id, run_id.
- `top_findings_by_blast_radius(n, filters)` — ranked backlog.
- `findings_by_triple(triple_id)` — all findings touching this triple.
- `findings_over_time(from_run, to_run)` — trend data.
- `heatmap(x_dim, y_dim)` — 2D count table, e.g., layer × defect_class.
- `regression_set(since_run)` — findings that transitioned to `regressed` since a run.
- `suppression_list()` — currently suppressed findings.
- `get_evidence(finding_id)` — full evidence including trace references.

### B7. Lifecycle transitions

External triage actions (via CLI or API):
- `triage(finding_id, assignee)` — status: new → triaged.
- `accept(finding_id, reason, defer_until?)` — status: → accepted.
- `suppress(finding_id, reason, expires_at?)` — status: → suppressed; reappearances remain suppressed until expiry or explicit unsuppress.
- `unsuppress(finding_id)` — status: → new or triaged.
- Findings transition to `fixed` automatically (B5) or manually.

Every transition writes to the `transitions` table with actor, reason, timestamp.

### B8. Run registration

Every simulator invocation opens a run:
```python
run_id = store.start_run(corpus_version, bpmn_version, simulator_version, taxonomy_version, config)
# ... simulation emits findings and traces ...
store.complete_run(run_id)
```

Incomplete runs (simulator crashed) are detectable — `completed_at IS NULL`. Reports filter them out by default.

### B9. Purge and retention

- Findings in `suppressed` status with expired suppression are reactivated on next run.
- Traces older than configured retention (default 90 days) are deleted, unless referenced by an unresolved finding.
- Runs older than retention have their trace files removed but run metadata preserved.

## Public API

```python
class FindingStore:
    def __init__(self, db_path: str): ...
    def start_run(self, corpus_version, bpmn_version, simulator_version, taxonomy_version, config) -> str: ...
    def complete_run(self, run_id: str): ...
    def emit_finding(self, finding: Finding) -> str: ...   # returns finding_id
    def record_trace(self, trace: Trace) -> str: ...
    def link_finding_to_trace(self, finding_id, trace_id, step_index): ...

    def compute_blast_radius(self, run_id: str): ...       # Batch, at end of run

    def get_findings(self, **filters) -> list[Finding]: ...
    def top_findings(self, n: int, **filters) -> list[Finding]: ...
    def findings_by_triple(self, triple_id: str) -> list[Finding]: ...
    def heatmap(self, x_dim: str, y_dim: str, **filters) -> dict: ...

    def triage(self, finding_id, assignee): ...
    def accept(self, finding_id, reason, defer_until=None): ...
    def suppress(self, finding_id, reason, expires_at=None): ...
    def unsuppress(self, finding_id): ...

    def detect_resolved(self, current_run_id: str): ...    # B5 logic
```

## What this component does NOT do

- Does not classify findings — component 11 does.
- Does not generate reports — component 13 does.
- Does not call LLMs.
- Does not modify triples or traces.

## Dependencies

- `contracts/finding-schema.md`, `contracts/trace-schema.md`.
- SQLite (v1) / Postgres (future).

## Verification

**V1.** Emit a finding twice from different runs; occurrence_count is 2, last_seen_run reflects the latest.

**V2.** Emit a finding, mark it fixed, then emit again; it transitions to regressed and regression_count becomes 1.

**V3.** Compute blast_radius on a test run where finding F appears in 3 of 10 traces: journeys_affected_pct = 0.3.

**V4.** `top_findings_by_blast_radius(5)` returns findings ordered by pct descending, secondary sort by severity.

**V5.** A suppressed finding with expired suppression is included in the next run's results.

**V6.** Querying by triple_id returns both primary and related triple findings.

**V7.** Heatmap(layer, defect_class) produces correct counts matching a direct SQL aggregate.

**V8.** Incomplete run (no complete_run call) is excluded from default reports but visible when explicitly queried.

## Implementation notes

- Use SQLite's JSON1 extension for evidence_json querying.
- Keep trace files on disk (not in DB) — reference by path. Database holds structured fields only.
- Batch inserts during simulation (don't commit per finding) for performance.
- Index on triple_id, defect_class, status is critical; add others as report builder queries reveal bottlenecks.
- Provide a CLI wrapper for triage actions so SMEs can work without the report UI.
- Migration strategy: every schema change bumps a store version; ship a migration script; old finding data is preserved, not rewritten.
