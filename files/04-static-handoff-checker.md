# Component 04 — Static Handoff Checker

## Purpose

For every direct edge (u → v) in the journey graph, check whether triple u's declared outputs formally satisfy triple v's declared inputs. No LLM, no execution — pure contract compatibility analysis. This is the cheapest, most deterministic layer of the simulator and catches the largest class of defects at near-zero cost.

## Inputs

- `JourneyGraph` from component 03.
- `TripleSet` (SimulationReadySet).

## Outputs

- `StaticCheckReport` — per-edge compatibility results.
- `Findings` emitted to finding store with `generator=static_handoff`.
- `Trace` records (mode=static) for each pair checked.

## Behavior

### B1. Pair enumeration

For each edge `(u, v)` in the graph:
- Load triple_u, triple_v.
- If either is excluded (per component 02's exclusion list), skip and record "skipped — triple excluded" in report.
- Otherwise, enqueue for checking.

For gateway nodes with multiple outgoing edges, each (gateway, successor) is one pair. The check verifies that regardless of which branch is taken, the consumer's contract is satisfiable from the gateway's output.

### B2. Contract compatibility rules

For each pair (u, v), run the following checks:

**C1 — Postcondition/precondition path alignment.** For every `path` in `v.pim.preconditions`, check that at least one triple on some path from a start event to u (inclusive of u) has that path in its `pim.postconditions` or `pim.state_writes`. If not → `state_flow_gap` finding on v.

**C2 — Type compatibility.** When a path is matched between producer postcondition and consumer precondition, verify the declared types are compatible. Strict: exact type match, or explicit subtype relationship. Mismatches → `type_mismatch` finding.

**C3 — Predicate satisfiability.** For consumer preconditions with non-trivial predicates (e.g., `in_range(0, 1000000)`), check that the producer's postcondition predicate (if any) is consistent. Examples:
- Producer says `value > 0`; consumer requires `value > 100`. Not provably satisfied → `state_flow_gap` (weak — producer may in practice produce >100 but hasn't declared it).
- Producer says `value in [low, high]`; consumer requires `value > threshold`. Check overlap.

This requires an expression evaluator — see B5.

**C4 — Obligation flow integrity.** For obligations opened by u, determine whether any downstream path from v can close them. If no reachable triple on any path closes the obligation, and v is not marked as exiting the journey with this obligation, → `orphan_obligation`.

**C5 — Naming drift detection.** Compare state path names across edges. If u writes `borrower.income` and v reads `borrower.incomeAmount`, heuristically flag as `handoff_naming_drift` (low confidence; for SME review).

**C6 — Format granularity check.** Same path, both sides; but one declares `timestamp` and the other `date`. Producer's finer-grained output may not match consumer's coarser-grained expectation, or vice versa. → `handoff_format_mismatch`.

### B3. Gateway-specific checks

For each gateway node u:

**G1 — Predicate partition check.** The predicates on u's outgoing edges must partition the context space:
- **Exclusive gateway:** predicates must be mutually exclusive and collectively exhaustive. If there is no default branch, the union of predicates must cover all inputs. Missing coverage → `predicate_non_partitioning` finding.
- **Parallel gateway:** all outgoing branches are always taken; no partition required but all must be reachable.

**G2 — Evidence presence.** Each branch predicate has `evidence_refs` pointing to triple content or regulatory refs justifying the predicate. Missing evidence → `content_missing` at PSM for the gateway triple.

**G3 — Default branch existence.** Recommend (not require) at least one default branch. Emit an observation, not a finding, if no default exists.

### B4. Expression evaluator (shared with other components)

Implement a minimal expression evaluator for predicates and assertions:

**Syntax supported:**
- Comparison: `==`, `!=`, `<`, `<=`, `>`, `>=`
- Boolean: `AND`, `OR`, `NOT`
- Membership: `IN`, `NOT IN`
- Existence: `EXISTS(path)`, `NOT EXISTS(path)`
- Arithmetic: `+`, `-`, `*`, `/`
- Functions: `within_business_days(n, anchor)`, `matches_pattern(regex)`, `in_range(low, high)`, `age_days(anchor)`
- Path references: dotted paths into journey state

**Evaluation modes:**
- `concrete(expr, state)` → returns bool or value given actual state.
- `symbolic(expr_producer, expr_consumer)` → returns one of `always_satisfied`, `never_satisfied`, `sometimes_satisfied`, `undetermined`.

The symbolic mode is used for static checks; concrete mode for sequence running.

If the evaluator cannot parse an expression, the predicate is flagged `evaluability_gap` on the containing triple.

### B5. Per-pair result emission

For each pair (u, v):
- Build a `StaticResult` record (see `contracts/trace-schema.md`).
- If any check fails, emit one finding per distinct failure, attributing to the relevant triple(s).
- Write trace record with mode=static.

### B6. Summary rollup

At end of run:
- Count pairs checked vs. skipped.
- Findings by class and by triple.
- Pairs with zero findings are the "clean handoffs" — reported as count for baseline tracking.

## Public API

```python
class StaticHandoffChecker:
    def __init__(self, graph: JourneyGraph, evaluator: ExpressionEvaluator): ...
    def check_all(self) -> StaticCheckReport: ...
    def check_pair(self, u: str, v: str) -> StaticResult: ...
    def check_gateway(self, gateway_id: str) -> StaticResult: ...
```

```python
class ExpressionEvaluator:
    def parse(self, expr: str) -> AST: ...
    def evaluate_concrete(self, ast: AST, state: dict) -> Any: ...
    def evaluate_symbolic(self, ast_producer: AST, ast_consumer: AST) -> SymbolicResult: ...
    def validate(self, expr: str) -> ParseResult: ...
```

## What this component does NOT do

- Does not call LLMs.
- Does not execute the triple's content — only its declared contracts.
- Does not generate personas or contexts — checks are context-free structural compatibility.
- Does not decide which branch a gateway would take on real data — only whether the predicates are structurally well-formed.

## Dependencies

- Component 03 (Journey Graph).
- `contracts/triple-schema.md`.
- `contracts/trace-schema.md`.
- `contracts/finding-schema.md`.
- Component 12 (Finding Store).

## Verification

**V1.** Given two triples u (writes `borrower.income: number`) and v (reads `borrower.income: number`), check reports clean handoff, zero findings.

**V2.** u writes `borrower.income: number`; v reads `borrower.income: string`. One `type_mismatch` finding on v.

**V3.** v reads `borrower.credit_score` but no upstream triple writes it. One `state_flow_gap` finding on v.

**V4.** Exclusive gateway with two branches whose predicates overlap. One `predicate_non_partitioning` finding on the gateway.

**V5.** Obligation opened at u, no triple downstream closes it, u does not mark exits_journey. One `orphan_obligation` finding on u.

**V6.** Gateway with predicate containing unparseable syntax. One `evaluability_gap` finding.

**V7.** Running check_all twice on the same inputs produces identical findings (determinism).

## Implementation notes

- Evaluator is a shared utility — extract into its own module so component 06 (Sequence Runner) can reuse for concrete evaluation.
- For symbolic evaluation, start conservative: when in doubt return `undetermined` rather than false positive. False negatives are discovered later by grounded testing; false positives burn SME review time.
- `check_all` should be parallelizable — each pair is independent.
- Cache expression parses; many predicates are reused across similar gateways.
- Pretty-print expression trees in trace output to aid human review.
