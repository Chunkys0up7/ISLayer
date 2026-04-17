# Component 08 — Branch Boundary Harness

## Purpose

At every gateway in the journey graph, construct contexts that deliberately stress decision boundaries: values at thresholds, just above/below boundaries, contexts that should force each branch deterministically, and ambiguous contexts where the correct branch is genuinely unclear. Detects `branch_misdirection`, `evaluability_gap`, and `escalation_failure` findings.

## Inputs

- `JourneyGraph`.
- Gateway list (derived from graph).
- For each gateway: its `BranchPredicate` set.
- LLM configuration.

## Outputs

- `BranchBoundaryReport` per gateway.
- Findings with `generator=branch_boundary`.
- Decision confidence metrics per gateway.

## Behavior

### B1. Per-gateway analysis

For each gateway u:

1. **Parse each branch predicate.** Use component 04's expression evaluator.
2. **Extract boundary variables.** A predicate like `apr_delta > 0.00125 AND product_type == "fixed"` has boundary variables:
   - `apr_delta` at the threshold 0.00125
   - `product_type` at each declared value
3. **Generate boundary contexts.** For each boundary variable, generate contexts that sit at the boundary and on either side:
   - `apr_delta = 0.00124` (just below)
   - `apr_delta = 0.00125` (at boundary — exact threshold case)
   - `apr_delta = 0.00126` (just above)
   - For enums: each discrete value.
4. **Generate ambiguous contexts.** Where the predicate has ambiguity (e.g., missing value, contradictory fields), construct contexts that exercise the ambiguity.

### B2. Run each context through the gateway

For each generated context:
1. Evaluate the predicate statically via component 04 → `static_branch`.
2. Execute the gateway triple via component 05 → `grounded_branch`.
3. Record:
   - `static_branch` (what the predicate says, as evaluated)
   - `grounded_branch` (what the LLM chose)
   - Agreement?
   - Evidence cited by the LLM.

### B3. Findings

- **Disagreement between static and grounded:** → `branch_misdirection` finding. Severity depends on which branch was wrong — if the static branch is the regulatorily-correct one and the LLM chose otherwise, severity = regulatory.
- **Exact-threshold ambiguity:** at the boundary, the predicate may evaluate differently depending on operator (`>` vs `>=`). If the declared predicate and the LLM's behavior suggest different operators were assumed, → `evaluability_gap` or `branch_misdirection`.
- **Escalation failure on ambiguous context:** if context is genuinely ambiguous (missing field, contradictory values), the LLM should detect it and escalate rather than guess. If it proceeds → `escalation_failure`.
- **Non-partitioning revealed:** if a context satisfies multiple predicates (overlap) or none (gap), confirming a static `predicate_non_partitioning` finding with a concrete example.

### B4. Gateway confidence metric

Per gateway, compute:
- `branch_agreement_rate` — fraction of contexts where static and grounded agreed.
- `boundary_stability` — fraction of boundary contexts where repeated runs produced the same choice.
- `escalation_appropriateness` — fraction of ambiguous contexts where the LLM correctly escalated.

Gateways with low scores on any metric are flagged as brittle decision points needing authoring attention.

### B5. Cross-branch regulatory check

For predicates tied to regulatory obligations:
- Verify each predicate's evidence_refs actually contains content that justifies the predicate. If the predicate says `within_business_days(3, application_received_at)` but the cited content describes a 30-day rule, → `content_stale` or `content_adjacent_not_actionable`.

## Public API

```python
class BranchBoundaryHarness:
    def __init__(self, graph: JourneyGraph, llm: LLMClient, evaluator: ExpressionEvaluator): ...
    def stress_gateway(self, gateway_id: str, seed_contexts: list[JourneyContext]) -> BranchBoundaryReport: ...
    def stress_all_gateways(self, persona_library: list[Persona]) -> list[BranchBoundaryReport]: ...
    def generate_boundary_contexts(self, gateway_id: str, base_context: JourneyContext) -> list[JourneyContext]: ...
```

## What this component does NOT do

- Does not test non-gateway handoffs — that's components 05/06/07.
- Does not generate arbitrary personas — uses the provided base contexts and constructs targeted boundary variants.
- Does not repair predicates.

## Dependencies

- Component 03 (Journey Graph).
- Component 04 (Expression Evaluator).
- Component 05 (Grounded Handoff Runner).
- Component 09 (Persona Generator) for base contexts.
- `contracts/finding-schema.md`.
- Component 12 (Finding Store).

## Verification

**V1.** Gateway with predicate `apr_delta > 0.00125`: harness generates contexts at 0.00124, 0.00125, 0.00126 and executes each. Static evaluations disagreeing with grounded produce findings.

**V2.** Gateway with overlapping predicates (both evaluate true on some context): harness finds a concrete context demonstrating the overlap. Finding `predicate_non_partitioning` with the example context attached.

**V3.** Gateway with a context where the key decision field is missing: harness runs, LLM either escalates (clean — no finding) or proceeds (finding `escalation_failure`).

**V4.** Gateway with predicate citing a stale regulatory reference: `content_stale` finding.

**V5.** Branch agreement rate computed correctly given N contexts.

## Implementation notes

- For continuous variables, be smart about boundary generation — use the units the domain actually uses (currency cents, not floats; days, not seconds — though this depends on the predicate).
- For exact-threshold cases, generate both `value == threshold` and `value == threshold ± epsilon` where epsilon is domain-appropriate.
- For compound predicates (`A AND B OR C`), generate contexts that exercise each sub-clause.
- Ambiguous context construction is the hardest part — consider a small library of ambiguity patterns: missing field, contradictory siblings, out-of-range values, null in non-nullable fields.
- Regulatory-severity branch misdirections should be promoted in the ranked backlog — these are the findings that cause real compliance risk.
