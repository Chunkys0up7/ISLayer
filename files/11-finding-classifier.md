# Component 11 — Finding Classifier

## Purpose

Take raw detection events from simulation components and classify them into the finding taxonomy. Separation from the simulation components keeps the taxonomy evolvable without touching simulation logic and enforces consistency: every finding in the store is classified by the same rules, regardless of which component detected it.

## Inputs

- `RawDetection` events emitted by simulation components (04, 05, 06, 07, 08, 10). Each carries:
  - `detector_id` — which component detected it.
  - `signal_type` — the primitive observation (e.g., "precondition_unmet", "undeclared_write", "isolation_divergence", "predicate_disagreement").
  - `context` — triple IDs, BPMN node/edge, trace reference, observed vs. expected.
- `TaxonomyConfig` — current taxonomy version and classification rules.

## Outputs

- `Finding` records conforming to `contracts/finding-schema.md`.
- Emitted to component 12 (Finding Store).

## Behavior

### B1. Classification pipeline

For each `RawDetection`:

1. **Resolve layer.** Based on detector and signal type:
   - Anything touching `cim.*` fields → CIM.
   - Anything touching `pim.preconditions`, `postconditions`, `predicates`, state paths → PIM.
   - Anything touching `psm.enriched_content`, content retrieval, LLM refusal about content → PSM.
   - Ambiguous signals default to PIM with a note for SME review.

2. **Resolve defect_class.** Map `signal_type` + `context` to exactly one class from the taxonomy. See the classification rules table below.

3. **Resolve severity.** Apply severity rules (B3).

4. **Resolve confidence.** Apply confidence rules (B4).

5. **Attribute triples.** Set `primary_triple_id` and `related_triple_ids`.

6. **Populate evidence.** Copy observed/expected, trace references, and produce a one-sentence `summary` and multi-sentence `detail`.

7. **Emit Finding.**

### B2. Classification rules table

The core mapping from signals to defect_class:

| detector | signal_type | context flag | defect_class | layer |
|----------|-------------|--------------|--------------|-------|
| 02 | identity_missing | — | `identity_incomplete` | (n/a) |
| 02 | layer_absent | layer=cim/pim/psm | `layer_missing` | that layer |
| 02 | intent_empty | — | `content_missing` | CIM |
| 02 | intent_multiline | — | `content_missing` | CIM |
| 02 | contract_fields_missing | — | `contract_missing` | PIM |
| 02 | gateway_no_predicates | — | `evaluability_gap` | PIM |
| 02 | obligation_unclosed | — | `orphan_obligation` | PIM |
| 02 | state_read_unproduced | — | `state_flow_gap` | PIM |
| 02 | content_empty | — | `content_missing` | PSM |
| 02 | predicate_unparseable | — | `evaluability_gap` | PIM |
| 02 | regulatory_ref_unresolved | — | `regulatory_orphan` | CIM |
| 02 | naming_drift_cluster | — | `handoff_naming_drift` | PIM |
| 03 | orphan_triple | — | `orphan_triple` | PIM |
| 03 | graph_structural | cycle | `journey_stuck` (risk) | PIM |
| 04 | precondition_unsatisfiable | type_mismatch | `type_mismatch` | PIM |
| 04 | precondition_unsatisfiable | path_absent | `state_flow_gap` | PIM |
| 04 | predicate_overlap | — | `predicate_non_partitioning` | PIM |
| 04 | predicate_gap | — | `predicate_non_partitioning` | PIM |
| 04 | obligation_unreachable_close | — | `orphan_obligation` | PIM |
| 04 | format_granularity | — | `handoff_format_mismatch` | PIM |
| 05 | undeclared_write | — | `output_under_declaration` | PIM |
| 05 | declared_write_absent | — | `output_over_promise` | PIM |
| 05 | undeclared_read | — | `input_under_declaration` | PIM |
| 05 | llm_refusal | reason_implies_content_gap | `content_missing` | PSM |
| 05 | llm_refusal | reason_implies_contract_gap | `contract_missing` | PIM |
| 05 | consumer_confusion | — | `handoff_format_mismatch` | PIM |
| 05 | implicit_setup | — | `handoff_implicit_setup` | PIM |
| 05 | branch_vs_predicate_disagree | — | `branch_misdirection` | PSM |
| 06 | silent_overwrite | — | `silent_overwrite` | PIM |
| 06 | obligation_deadline_passed | — | `regulatory_violation` | CIM |
| 06 | loop_detected | — | `journey_stuck` | PIM |
| 06 | context_unbounded_growth | — | `context_bloat` | PSM |
| 06 | late_journey_drift | — | `cumulative_drift` | PIM |
| 07 | isolation_divergence | — | `handoff_carried_by_external_context` | PIM |
| 08 | branch_disagreement_boundary | — | `branch_misdirection` | PSM |
| 08 | ambiguity_not_escalated | — | `escalation_failure` | PSM |
| 08 | predicate_cites_stale_content | — | `content_stale` | PSM |
| 10 | perturbation_not_detected | expected=halt, actual=continued | `escalation_failure` | PSM |
| 10 | perturbation_wrong_output | — | `cumulative_drift` or `correctness` case | PIM |
| 10 | ablation_blast_radius_high | — | (observation only, not a finding) | — |
| 10 | ablation_blast_radius_zero | — | (observation only, candidate for cleanup) | — |

### B3. Severity rules

Apply in order; first match wins:

1. If the finding involves an unclosed regulatory obligation, a deadline violation, or a branch misdirection on a regulatory predicate → **regulatory**.
2. If `defect_class ∈ {branch_misdirection, type_mismatch, output_over_promise, handoff_format_mismatch, silent_overwrite, cumulative_drift}` and the affected triple is on the critical path → **correctness**.
3. If `defect_class ∈ {handoff_carried_by_external_context, input_under_declaration, output_under_declaration}` → **correctness**. (These are high-priority structural issues even if journeys currently complete.)
4. If `defect_class ∈ {context_bloat, handoff_naming_drift, orphan_triple}` → **efficiency**.
5. All other classes → **cosmetic** if off critical path, **efficiency** if on critical path.

Severity can be overridden per finding by an SME during triage (stored as `severity_override` alongside the rule-derived severity).

### B4. Confidence rules

- Static detectors (02, 03, 04) → always **high**.
- Grounded detectors (05, 06, 07, 08) → **high** if consistent across all N repeat runs; **medium** if consistent across > 50%; **low** otherwise.
- Perturbation/ablation (10) → inherit confidence from the underlying runner.
- First-observation signals with no prior baseline → **low** until re-detected.

### B5. Deduplication

Before emitting a finding, check the store (component 12) for an existing finding with:
- Same `defect_class`
- Same `primary_triple_id` (and ideally `related_triple_ids`)
- Same taxonomy_version

If found:
- Increment `occurrence_count`.
- Update `last_seen_run`.
- Keep the original `finding_id`.
- Update confidence and blast radius if they've shifted.
- If previous status was `fixed` and now re-detected → transition to `regressed`, increment a `regression_count`.

If not found, emit a new Finding.

### B6. Summary and detail generation

- `summary` is a one-sentence human-readable description, templated per defect_class:
  - `handoff_carried_by_external_context`: "Handoff from {u} to {v} relies on context outside the declared contract."
  - `state_flow_gap`: "Triple {v} reads state path {path}, but no upstream triple writes it."
  - etc.
- `detail` is 2-4 sentences including: what was observed, what the contract said, which trace shows the evidence.

Generation is templated — no LLM involvement, for determinism.

## Public API

```python
class FindingClassifier:
    def __init__(self, taxonomy: TaxonomyConfig, store: FindingStore): ...
    def classify(self, detection: RawDetection) -> Finding: ...
    def classify_batch(self, detections: list[RawDetection]) -> list[Finding]: ...
    def reclassify_all(self, old_taxonomy_version: str, new_taxonomy_version: str) -> ReclassifyReport: ...
```

## What this component does NOT do

- Does not detect anything itself — it only classifies detections.
- Does not call LLMs.
- Does not modify the store beyond emitting findings (the store handles persistence).
- Does not decide which findings are false positives — suppression is SME-driven.

## Dependencies

- `contracts/finding-schema.md`.
- Taxonomy config file (versioned YAML).
- Component 12 (Finding Store) — for dedup lookup.

## Verification

**V1.** A `RawDetection` from component 04 with signal_type=predicate_overlap produces exactly one Finding with defect_class=`predicate_non_partitioning`, layer=PIM, severity=correctness (if critical path) or efficiency, confidence=high.

**V2.** A RawDetection from component 07 with signal_type=isolation_divergence produces Finding with defect_class=`handoff_carried_by_external_context`, layer=PIM, confidence high if repeated, medium otherwise.

**V3.** Emitting the same detection twice: on second emit, occurrence_count is 2, finding_id is unchanged, last_seen_run updated.

**V4.** A previously-`fixed` finding reappearing transitions to `regressed` and increments regression_count.

**V5.** Taxonomy version change triggers reclassify_all; findings whose class mapping changed are updated; old and new taxonomy_version are recorded in an audit log.

**V6.** Severity rules: a regulatory-boundary branch misdirection gets severity=regulatory regardless of critical path status.

## Implementation notes

- Classification rules should live in a YAML config, not hardcoded. This allows tuning without code changes.
- Keep the summary/detail templates in the same config — editing copy should not require deploying code.
- Reclassification is infrequent but important; make it a batch job separate from normal operation.
- When a new detector is added (e.g., a new component 14), it must register its signal_types in the classification config before emitting. Enforce this in the classifier — unknown signal_types raise a configuration error rather than silently producing misclassified findings.
- Log every classification decision to an audit trail. Not for user consumption, but for debugging taxonomy drift later.
