# Component 10 — Perturbation and Ablation Generator

## Purpose

Take an existing clean run (trace + persona + corpus) and mutate one thing — either a context field or a triple — then re-run to see what breaks. Perturbation stresses the process's robustness to realistic input variance; ablation tests the corpus's load-bearing structure.

## Inputs

- A baseline `Persona`.
- The `TripleSet`.
- The `JourneyGraph`.
- Mutation config.

## Outputs

- `PerturbedPersona` objects — each derived from a baseline persona with one mutation.
- `AblatedCorpus` objects — each derived from the baseline TripleSet with one triple or content chunk removed.
- Findings emitted with `generator=perturbation` or `generator=ablation`.
- An Ablation Blast Radius report: for each ablation, which journeys fail and how.

## Behavior

### B1. Field perturbation

Given a baseline persona, for each configured mutation class, generate perturbed variants:

**Mutation classes:**
- `null_field(path)` — set a field to null.
- `flip_boolean(path)` — invert a boolean field.
- `boundary_flip(path)` — move a numeric value across a known threshold.
- `type_error(path)` — set a field to a value of the wrong type.
- `out_of_range(path)` — set a numeric field outside declared bounds.
- `date_shift(path, delta)` — move a timestamp by a configured amount (e.g., ±1 business day).
- `enum_swap(path)` — change an enum to a different valid value.
- `contradict(path_a, path_b)` — set two dependent fields to inconsistent values.

Each mutation produces one `PerturbedPersona` with:
- `base_persona_id`
- `mutation: {class, path, from_value, to_value, rationale}`
- `expected_behavior: enum: detect_and_halt | detect_and_reroute | continue_with_warning | regulatory_violation`

`expected_behavior` is declared by the person configuring the perturbation — it's the oracle for this test. If the simulator's outcome differs from expected, that's a finding.

### B2. Triple ablation

Given the TripleSet, for each ablation mode:

**Ablation modes:**
- `remove_triple(triple_id)` — remove one triple entirely. Journey stuck on reaching its node.
- `remove_content_chunk(triple_id, chunk_id)` — remove one piece of enriched content. Tests whether the triple's remaining content is sufficient.
- `remove_regulatory_ref(triple_id, ref_id)` — strip a regulatory reference. Tests whether the triple still enforces the rule.
- `remove_predicate(gateway_id, edge_id)` — drop one branch predicate. Tests whether the gateway still partitions the space.

Each ablation produces an `AblatedCorpus` carrying the modified TripleSet and:
- `ablation: {mode, target_id, rationale}`.

### B3. Run baseline personas against ablated corpora

For each ablation:
- Re-run all baseline personas against the ablated TripleSet (using component 06 sequence runner in static or grounded mode as configured).
- Compare outcomes to the baseline (unablated) traces.
- Record which personas/journeys now fail, and how.

This produces the **blast radius per ablation**: number of journeys affected, severity of failures.

### B4. Blast radius analysis

Across all ablations:
- Rank triples by blast radius (ablation of triple T breaks N journeys).
- Rank content chunks by blast radius.
- Identify load-bearing triples (high blast) vs. rarely-touched triples (low blast).
- Low-blast triples are candidates for deletion or merging — emit observation (not finding) for SME review.
- High-blast triples are the most important to keep well-maintained — highlight in the report.

### B5. Perturbation run

For each perturbed persona:
- Run the journey (via component 06).
- Record outcome.
- Compare outcome to `expected_behavior`:
  - Matched → no finding.
  - Mismatch — persona expected `detect_and_halt` but journey continued → finding depends on severity: if a regulatory obligation was active, `regulatory_violation`; otherwise `escalation_failure` or `cumulative_drift`.
  - Journey continued but produced wrong output → `correctness`-severity finding.

### B6. Reporting

- Perturbation report: per mutation class, success rate in detecting/handling. A simulator that handles `null_field` on critical fields gracefully is robust; one that silently proceeds is fragile.
- Ablation report: per triple and content chunk, blast radius. Used to rank authoring priority and identify the load-bearing subset of the corpus.

## Public API

```python
class PerturbationGenerator:
    def __init__(self, graph: JourneyGraph, triple_set: TripleSet, config: PerturbConfig): ...
    def perturb(self, base_persona: Persona, classes: list[MutationClass] = None) -> list[PerturbedPersona]: ...

class AblationGenerator:
    def __init__(self, triple_set: TripleSet, graph: JourneyGraph): ...
    def ablate_triples(self) -> list[AblatedCorpus]: ...
    def ablate_content(self) -> list[AblatedCorpus]: ...
    def ablate_regulatory(self) -> list[AblatedCorpus]: ...
    def run_ablation_sweep(self, baseline_personas: list[Persona], runner: SequenceRunner) -> AblationReport: ...
```

## What this component does NOT do

- Does not perturb triples and personas in the same mutation — one change at a time, isolated.
- Does not repair anything.
- Does not decide what "correct" behavior is — relies on `expected_behavior` declarations.

## Dependencies

- Component 03 (Journey Graph).
- Component 06 (Sequence Runner).
- Component 09 (Persona Generator) — for baseline personas to perturb.
- `contracts/journey-context.md`, `contracts/finding-schema.md`.
- Component 12 (Finding Store).

## Verification

**V1.** `null_field` perturbation on a critical field: journey either halts/escalates (clean) or continues inappropriately (finding).

**V2.** Triple ablation sweep: removing each triple in turn produces a blast-radius table. Triples marked as low-blast (< 5% of journeys affected) are flagged for SME review.

**V3.** Boundary_flip mutation on a known regulatory threshold: expected behavior is specified; mismatches emit findings.

**V4.** Determinism: same mutation config + seed + persona produces identical perturbed personas.

**V5.** Content chunk ablation: removing one chunk from a triple's content still allows the triple to execute (some chunks are redundant) or fails to execute (that chunk was load-bearing). Either way, the blast radius metric is computed correctly.

## Implementation notes

- Ablation sweeps are expensive (each ablation re-runs all baseline journeys). Scale by running sweeps in static mode first (component 04), escalating to grounded only for ablations that show interesting static effects.
- Perturbation expected-behavior declarations should live in the persona library alongside canonical personas — SMEs maintain both together.
- Consider randomized ablation sampling for very large corpora: rather than ablating every chunk, sample N and extrapolate blast radius.
- Report ablation results as both: per-triple blast (how many journeys fail when T is removed) and per-journey vulnerability (how many different ablations break journey J — journeys vulnerable to many ablations are brittle paths).
