# Component 09 — Persona Generator

## Purpose

Produce seed contexts (personas) for the simulator to run against. Personas are structured starting states representing realistic and edge-case inputs to the journey. Deterministic given a seed.

## Inputs

- `JourneyGraph` — to understand what state fields the journey might require.
- `TripleSet` — to find what input fields are referenced anywhere.
- A persona library (handcrafted canonical personas for happy-path testing).
- Generation config: seed, number to generate, coverage targets.

## Outputs

- `Persona` objects each containing:
  - `persona_id: string`
  - `name: string` (human-readable label)
  - `category: enum: canonical | boundary | adversarial | random_valid | historical`
  - `seed_context: JourneyContext` (initial state — the starting `state` object)
  - `metadata: dict` (which branches this persona is expected to take, regulatory conditions it satisfies, etc.)
- A `PersonaManifest` listing all generated personas with their coverage.

## Behavior

### B1. Canonical personas

From the persona library, load handcrafted personas representing:
- Each primary happy-path scenario (e.g., "clean W-2 borrower, conforming loan")
- Each major exception class (e.g., "self-employed", "non-US-resident", "jumbo loan")

These are authored once and versioned. They form the stable baseline against which regressions are detected.

### B2. Boundary persona generation

For each regulatory rule in the corpus (found via `cim.regulatory_refs` with thresholds or timing anchors), generate personas that sit at the boundary:
- TRID timing: `application_received_at` = 4:59 PM Friday before federal holiday.
- APR tolerance: `apr_delta` = 0.00125 exactly.
- Income thresholds: value at each defined break.
- Age/date boundaries: anchor = rule date ± one day.

### B3. Random valid personas

Generate N valid personas by sampling within declared ranges. Used for volume runs:
- Each state field is sampled from a distribution (uniform within range, or from a discrete value set).
- Constraints preserved: if field B depends on field A, generation respects the dependency.
- Seed-deterministic.

### B4. Adversarial personas

Constructed to stress specific defect classes:
- **Contradiction:** contexts with conflicting field values (e.g., `borrower.age = 25` and `borrower.retirement_income > 0`).
- **Missing critical:** contexts missing one field that no triple explicitly requires but one later triple implicitly needs.
- **Near-duplicate:** two personas differing by one value, to test sensitivity.

### B5. Historical personas (optional)

If a file of real historical cases is provided (with PII stripped), convert them to personas. These are the highest-fidelity test data:
- Parse the historical input (CSV, JSON, or specified format).
- Map fields to the state schema.
- Tag with `category=historical`.

### B6. Coverage tracking

For each persona, record which:
- BPMN paths it is expected to traverse.
- Regulatory obligations it should trigger.
- Gateway branches it should cause.

At generation end, produce coverage metrics: % of BPMN paths covered, % of gateway branches covered, % of regulatory rules boundary-tested.

### B7. Manifest and reproducibility

Emit a `PersonaManifest` with seed, config, and list of personas. Persona library version is recorded. Re-running with same seed and library produces identical personas.

## Public API

```python
class PersonaGenerator:
    def __init__(self, graph: JourneyGraph, triple_set: TripleSet, library: PersonaLibrary, config: GenConfig): ...
    def generate_canonical(self) -> list[Persona]: ...
    def generate_boundary(self, seed: int) -> list[Persona]: ...
    def generate_random_valid(self, n: int, seed: int) -> list[Persona]: ...
    def generate_adversarial(self, seed: int) -> list[Persona]: ...
    def load_historical(self, path: str) -> list[Persona]: ...
    def generate_all(self, seed: int) -> PersonaManifest: ...
```

## What this component does NOT do

- Does not perturb existing personas — that's component 10.
- Does not run simulation.
- Does not guarantee persona realism beyond schema conformance — SMEs curate the canonical library.

## Dependencies

- Component 03 (Journey Graph).
- `contracts/journey-context.md`.
- Persona library (external file or directory of YAML/JSON definitions).
- Historical data source (optional, external).

## Verification

**V1.** Canonical personas load from library and conform to the journey context schema.

**V2.** Boundary personas for a rule with threshold 0.00125 include contexts at 0.00124, 0.00125, 0.00126.

**V3.** Random_valid generation with seed S produces identical personas on re-run.

**V4.** Coverage metrics: given a journey with 3 gateways × 2 branches each, the generated persona set covers all 6 branches (verified by static predicate evaluation over each persona).

**V5.** Adversarial persona with contradictory fields is correctly flagged as `category=adversarial`.

## Implementation notes

- Persona library should be a directory of YAML files under version control, reviewed by SMEs.
- For boundary generation, extract thresholds from predicate expressions — this requires parsing predicates (component 04's evaluator) and walking the AST for comparison operators with literal operands.
- Historical data ingestion must preserve the mapping from historical field names to schema paths — keep this mapping in a separate config file per data source.
- Persona manifest is a first-class artifact referenced in every trace for reproducibility.
- When generating random valid personas, avoid generating values that would never occur in practice (e.g., credit scores of 2000) — use realistic distributions per field.
