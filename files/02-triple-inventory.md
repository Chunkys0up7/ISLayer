# Component 02 — Triple Inventory

## Purpose

Before any simulation runs, produce a comprehensive completeness and consistency report on the triple set. This is the simulator's **first value delivery** — most initial findings come from here, at zero LLM cost. The inventory also gates simulation: triples that fail critical invariants are excluded from downstream components.

## Inputs

- `TripleSet` produced by component 01.
- Optional: `previous_inventory.json` — last inventory snapshot, for trend detection.

## Outputs

- `InventoryReport` — a structured report (JSON + markdown) containing:
  - Per-triple field completeness matrix
  - Invariant violations per triple (findings)
  - Cross-triple consistency checks
  - Contract declaration coverage statistics
  - Exclusion list (triples not ready for simulation)
- `Findings` emitted to the finding store (component 12) with `generator=inventory`.
- `SimulationReadySet` — subset of TripleSet whose triples pass critical invariants (I1–I4).

## Behavior

### B1. Field completeness matrix

For every triple, check presence of every required field from `contracts/triple-schema.md`. Produce a matrix:

```
triple_id | cim.intent | cim.regulatory_refs | pim.preconditions | pim.postconditions | ...
T001      | ✓          | ✓                    | ✓                  | ✓                   | ...
T002      | ✓          | ✗                    | ✓                  | ✗                   | ...
```

Populate the matrix with one of: `✓` (present and non-empty), `○` (present but empty list/object), `✗` (missing entirely).

### B2. Invariant enforcement

Run each invariant I1–I10 across the triple set:

- **I1 (identity completeness):** per-triple check. Violations → finding class `identity_incomplete`, severity `correctness`, included in exclusion list.
- **I2 (layer presence):** per-triple check. Violations → finding class `layer_missing`.
- **I3 (intent statement):** per-triple check. Empty or multi-sentence intents → finding class `content_missing` at CIM.
- **I4 (contract declaration):** per-triple check. Missing contract fields → finding class `contract_missing`, included in exclusion list.
- **I5 (gateway predicates):** for gateways only. Missing predicates → `evaluability_gap`.
- **I6 (obligation closure):** cross-triple. For each obligation_id in any `obligations_opened`, verify it appears in some `obligations_closed` or `exits_journey=true`. Orphans → `orphan_obligation`.
- **I7 (state-flow referential integrity):** cross-triple. For each path in `preconditions` or `state_reads`, verify it is produced by some upstream triple. Requires BPMN graph (passed in via component 03, see dependency note). Violations → `state_flow_gap`.
- **I8 (content presence):** per-triple for task/gateway nodes. Empty enriched_content → `content_missing` at PSM.
- **I9 (predicate evaluability):** per gateway. Parse each `predicate_expression` via the evaluator (component 04's parser). Unparseable → `evaluability_gap`.
- **I10 (regulatory resolution):** per-triple. Every obligation's `regulatory_ref` must resolve to declared `cim.regulatory_refs`. Violations → `regulatory_orphan`.

### B3. Cross-triple consistency checks

Beyond invariants, run several consistency checks:

- **Naming drift detection:** cluster state field paths by similarity (e.g., `borrower.income.amount` vs. `borrower.income_amount`). Suspicious clusters → `handoff_naming_drift` (low confidence, for SME review).
- **Orphan triples:** triples not referenced by the BPMN graph (no corresponding node). Requires component 03. Violations → `orphan_triple`.
- **Duplicate BPMN bindings:** two triples pointing at the same `bpmn_node_id` with overlapping intent. Emit observation (not finding) for SME review.
- **Content-intent consistency spot check (optional, LLM-backed):** for a sampled subset, verify that enriched content contains information relevant to the stated intent. Gated by config flag because it costs LLM calls. Violations → `content_adjacent_not_actionable`.

### B4. Trend detection (if previous inventory provided)

Compare current inventory to previous:

- Newly-missing fields per triple (regression in authoring).
- Newly-added triples (growth of corpus).
- Removed triples (check: are any findings against them now orphaned?).
- Invariant violation count delta (improving or degrading).

### B5. Exclusion list generation

Triples failing I1 or I4 are excluded from `SimulationReadySet`. Their triple_ids are written to the exclusion list with exclusion reason. Downstream components must check this list before operating on a triple.

Triples failing I2, I3, or I5–I10 are **included** in SimulationReadySet — the violations are findings, but the triples are still simulatable to whatever extent possible.

## Public API

```python
class TripleInventory:
    def __init__(self, triple_set: TripleSet, graph: Optional[JourneyGraph] = None): ...
    def run(self) -> InventoryReport: ...
    def get_simulation_ready_set(self) -> TripleSet: ...
    def get_exclusions(self) -> list[ExclusionRecord]: ...
```

Note: `graph` parameter is optional to allow inventory to run before component 03 is built (in early Phase 1). When graph is None, invariants I6, I7, and the orphan-triple check are deferred with a warning in the report.

## What this component does NOT do

- Does not execute any triples.
- Does not call LLMs (except for optional B3 content-intent spot check).
- Does not modify triples — read-only operation.
- Does not assign severity beyond the defaults per defect class.

## Dependencies

- Component 01 (Triple Loader) — provides TripleSet.
- Component 03 (Journey Graph) — optional but needed for full invariant coverage.
- `contracts/triple-schema.md` — invariants.
- `contracts/finding-schema.md` — finding output format.
- Component 12 (Finding Store) — where findings are emitted.

## Verification

**V1.** On a test corpus where all triples conform to schema, InventoryReport shows 100% completeness and zero findings.

**V2.** On a test corpus with one triple missing `cim.intent`, one missing `pim.preconditions`, and one gateway without predicates, report shows exactly three findings of classes `content_missing`, `contract_missing`, `evaluability_gap` respectively.

**V3.** On a corpus with an obligation opened in triple T1 and never closed, report contains one `orphan_obligation` finding on T1.

**V4.** On a corpus where T2 reads `borrower.credit_score` but no triple writes it, report contains one `state_flow_gap` finding on T2.

**V5.** Exclusion list matches exactly the triples violating I1 or I4.

**V6.** Given the same corpus, two runs produce identical reports (determinism check).

**V7.** With a previous_inventory passed in and one field newly added to one triple, the trend section shows exactly that delta.

## Implementation notes

- Matrix rendering should support both JSON (for machine processing) and markdown table (for human review).
- On a corpus of 100+ triples, use colored terminal output for the completeness matrix to catch attention.
- Make the B3 LLM-backed content-intent check optional and off by default — it's a separate feature behind a config flag.
- Inventory report should carry the `corpus_version_hash` from component 01 to enable trend comparison.
- Keep invariants as pure functions of TripleSet (+ optionally graph) so they're independently unit-testable.
