# Component 13 — Report Builder

## Purpose

Produce the artifacts that humans and downstream systems consume: the ranked defect backlog, layer-class heatmaps, trend reports, regression dossiers, and run summaries. This is where the simulator's value reaches the authoring team.

## Inputs

- `FindingStore` (queryable).
- A run_id (or a range of run_ids for trend reports).
- Report configuration: which reports to produce, output formats, filter overrides.

## Outputs

All reports are emitted as files under `reports/<run_id>/`:

- `backlog.md` — human-readable ranked defect backlog.
- `backlog.json` — machine-readable backlog for downstream tools.
- `backlog.csv` — same data, spreadsheet-friendly.
- `heatmap_layer_class.md` — layer × defect_class matrix with counts.
- `heatmap_generator_class.md` — generator × defect_class matrix.
- `trend.md` — run-over-run trend on key metrics.
- `regressions.md` — findings newly regressed since last run.
- `run_summary.md` — one-page summary of this run.
- `triple_dossier/<triple_id>.md` — per-triple page listing all findings touching it (optional, for heavily-affected triples).

## Behavior

### B1. Ranked backlog

Query `top_findings_by_blast_radius(n=default_cap, filters={confidence: [high, medium], status: [new, triaged, regressed]})`.

Default cap = 20. Configurable via report config.

Sorting:
1. Severity descending (`regulatory > correctness > efficiency > cosmetic`).
2. Within severity: blast radius descending.
3. Within blast radius: occurrence_count descending.

Each backlog entry includes:
- Rank
- Finding ID
- Summary
- Layer, defect_class, severity, confidence
- Primary triple + link to dossier
- Blast radius (count + pct)
- First seen run, occurrence count
- Detail (collapsed by default in markdown)
- Trace evidence link

Markdown format:

```markdown
# Ranked Defect Backlog — Run {run_id}

Produced: {timestamp}
Corpus version: {corpus_version}
Total findings: {total}  |  Shown: top {cap}

## 1. [REGULATORY] Handoff from T023 to T024 relies on context outside declared contract

- **Finding:** F-7291a
- **Layer:** PIM  |  **Class:** handoff_carried_by_external_context
- **Confidence:** high  |  **Generator:** context_isolation
- **Primary triple:** T023 (also affects T024)
- **Blast radius:** 47 / 120 journeys (39%)  |  **Critical path:** yes
- **First seen:** run 2026-03-15  |  **Occurrences:** 4 runs
- **Summary:** Under isolation, T024 cannot complete from T023's declared outputs alone; full-content runs succeed. Handoff is load-bearing on T023's PSM content not declared as state write.
- [Evidence](traces/T-5512.json) | [Triple dossier](triple_dossier/T023.md)

## 2. [CORRECTNESS] ...
```

### B2. Heatmaps

Produce 2D count tables for:
- Layer × defect_class
- Generator × defect_class
- Severity × status
- Triple (top 20 by finding count) × defect_class

Rendered as markdown tables with colored cells (severity-gradient) and also as CSV.

```markdown
|          | CIM | PIM | PSM |
|----------|-----|-----|-----|
| content_missing | 3 | - | 12 |
| state_flow_gap | - | 18 | - |
| ...
```

### B3. Trend report

Query the last N runs (default 10). For each metric, plot the series:

- Total findings
- Findings by layer
- Findings by severity
- New findings per run
- Regressed findings per run
- Resolved findings per run
- Clean handoff count (from static checks)
- Isolation divergence count (from component 07)

Output: markdown tables with simple ASCII sparklines, plus a JSON series file for external plotting.

Highlight:
- Metrics trending worse (red flag).
- Metrics trending better (green flag).
- Sudden jumps (potential regression or new defect class).

### B4. Regression report

Query `regression_set(since_run=last_run_id)`. For each regressed finding:

- Current state
- When it was previously fixed
- What changed between then and now (corpus version diff — if the store tracks it, include changed triples between the fixed-run and the current run)
- Evidence pointer

Regression reports get their own file because they're the most important thing a SME sees after a run. A regression means an authoring change broke something previously verified.

### B5. Run summary

One-page markdown:
- Run metadata (versions, duration, config)
- Counts: total findings, by severity, by layer, new vs. regressed vs. persistent
- Top 5 backlog entries
- Delta vs. previous run
- Budget consumed (LLM tokens, cost) if grounded modes were run
- Notable events: new defect classes encountered, ablation sweep results, calibration runs

This is the first thing a lead reviews; it should fit in one screen.

### B6. Triple dossier (on demand)

For any triple with ≥ 3 findings, generate a dossier file listing:
- Triple metadata (ID, BPMN node, version)
- All findings touching this triple (sorted by severity)
- Upstream/downstream neighbors in the graph
- Recent trace references involving this triple
- Historical finding timeline on this triple

Useful for SME authoring sessions — open the dossier, fix everything about that triple in one pass.

### B7. Filtered views

Reports support filter overrides via config:
- Show only CIM findings
- Show only regulatory severity
- Show only findings on a specific BPMN lane
- Exclude specific defect classes (e.g., hide all `handoff_naming_drift` while the team prioritizes other classes)

Filters are declared in the report config and the applied filters are shown in each report header so results aren't misread.

### B8. SME action hooks

Each backlog entry includes a suggested next action derived from the defect_class:

- `contract_missing` → "Author pre/post conditions for this triple."
- `handoff_carried_by_external_context` → "Declare the fields producer writes that consumer currently reads undeclared."
- `evaluability_gap` → "Express gateway decision as evaluable predicate."
- `orphan_obligation` → "Identify the closing step or mark this obligation as exits_journey."

Suggestions come from a config file, are templated per class, and are advisory (not required).

## Public API

```python
class ReportBuilder:
    def __init__(self, store: FindingStore, config: ReportConfig): ...
    def build_all(self, run_id: str) -> ReportBundle: ...
    def build_backlog(self, run_id: str, cap: int = 20, filters: dict = None) -> Path: ...
    def build_heatmaps(self, run_id: str) -> list[Path]: ...
    def build_trend(self, last_n_runs: int = 10) -> Path: ...
    def build_regressions(self, since_run: str) -> Path: ...
    def build_run_summary(self, run_id: str) -> Path: ...
    def build_triple_dossier(self, triple_id: str) -> Path: ...
```

## What this component does NOT do

- Does not modify findings.
- Does not call LLMs.
- Does not provide a live UI — reports are files. A UI is a separate downstream system that consumes the JSON outputs.
- Does not make triage decisions — it presents data.

## Dependencies

- Component 12 (Finding Store).
- `contracts/finding-schema.md`.
- A markdown + CSV writer.
- Optional: a simple JSON-to-sparkline renderer for trend.

## Verification

**V1.** Given a store with 50 findings, build_backlog with cap=10 produces a markdown file with 10 entries, correctly ordered by severity then blast_radius.

**V2.** Heatmaps sum to the total finding count in the filtered set.

**V3.** Trend report over 5 runs with a deliberate regression shows the regression at the correct run.

**V4.** Regression report includes only findings transitioned to `regressed` since the specified run.

**V5.** Run summary on a run with 0 findings produces a valid report noting the clean state, not a blank file.

**V6.** Triple dossier on a triple with 5 findings includes all 5 in severity order.

**V7.** Filter `severity=regulatory` produces a backlog containing only regulatory-severity findings.

**V8.** All output files are valid markdown / CSV / JSON — verified by format linters.

## Implementation notes

- Keep rendering separate from data gathering. Build a `ReportData` intermediate object, then render to markdown/CSV/JSON from it. This makes new formats easy to add.
- Markdown tables get hard to read above ~20 rows — use collapse/fold in the markdown where supported, or paginate.
- When rendering trace links, use relative paths so reports are portable across environments.
- SME action hooks are the single highest-leverage feature for adoption. Invest in the config file that maps defect_class → action — these are the suggestions that turn findings into fixes.
- Regression report format should highlight at the top: "X findings regressed since last run" with the triple(s) responsible. This is the "read this first" artifact.
- For very large runs (thousands of findings), generate a summary report inline and provide the full backlog as JSON download only — the markdown version would be unreadable.
