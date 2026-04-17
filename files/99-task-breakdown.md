# 99 — Task Breakdown

Ordered, dependency-aware implementation plan for Claude Code. Four phases, each delivering standalone value. Stop at the end of any phase and you have a useful tool; continue and you extend it.

Every task below follows the spec-driven-dev task template: Context, Action, Verify, Depends.

---

## Phase 1 — Foundation (Inventory delivers first value)

**Goal:** Ingest triples, produce a completeness and consistency report without any simulation. This phase alone surfaces the largest batch of initial findings.

**Components:** 01, 02, 03 (partial), plus contracts and finding store skeleton.

### Task 1.1: Project scaffolding
**Context:** Every component depends on shared project structure, configuration loading, and logging. Establishing this first prevents rework across subsequent tasks.
**Action:** Create Python package structure (`triple_flow_sim/`), `pyproject.toml`, basic logging config, a `config.py` that loads YAML config files. Install core deps: `pyyaml`, `networkx`, `pydantic`, `click`, `pytest`.
**Verify:** `python -m triple_flow_sim --version` prints a version; tests directory runs an empty test suite successfully.
**Depends:** none.

### Task 1.2: Contract models (Pydantic)
**Context:** Every component reads/writes data conforming to the contracts. Implementing these as Pydantic models gives free validation and serialization.
**Action:** Implement Pydantic models for `Triple`, `TripleSet`, `JourneyContext`, `Finding`, `Trace`, `TraceStep`, `BranchPredicate`, `ContextAssertion`, `ObligationSpec`, `StateFieldRef`, `ContentChunk`. Include JSON schema generation for external docs.
**Verify:** Round-trip test: load a sample triple YAML, serialize to JSON, parse back, verify equality. Pydantic validation rejects malformed inputs with clear errors.
**Depends:** 1.1.

### Task 1.3: Finding store (SQLite skeleton)
**Context:** Components 02-onwards emit findings. Even Phase 1 needs a place to store them. Build minimal store now, extend in Phase 4.
**Action:** Implement component 12 at ~40% scope: SQLite schema migration, `start_run`, `complete_run`, `emit_finding` with dedup, basic `get_findings` and `findings_by_triple`. Skip blast radius computation and lifecycle transitions for now.
**Verify:** Emit the same finding twice from two runs; query returns one finding with occurrence_count=2. Database is created at the configured path and schema matches spec.
**Depends:** 1.2.

### Task 1.4: Triple loader — core
**Context:** Start of the data pipeline. Must handle the actual format triples are in today.
**Action:** Implement component 01 for `yaml_per_triple` and `json_per_triple` formats. Include git clone integration, field_mapping, identity validation (I1), corpus_version_hash, on-disk cache. Skip `markdown_frontmatter` and `custom_jsonl` formats for v1.
**Verify:** Run all V1–V5 verifications from component 01 spec against a test fixture corpus (10 triples, 2 malformed, 1 with missing identity).
**Depends:** 1.2.

### Task 1.5: Expression evaluator (parse-only)
**Context:** Component 02 invariant I9 requires parsing predicates. Component 04 and 06 will execute them. Build the parser first; execution comes later.
**Action:** Implement `ExpressionEvaluator.parse(expr) -> AST` and `validate(expr) -> ParseResult`. Support the syntax listed in component 04 B4 (comparisons, boolean ops, membership, existence, path refs, functions). Use a PEG parser (lark) or handwritten recursive descent.
**Verify:** Parse a battery of valid expressions (~20 examples) into correct ASTs. Invalid expressions (typos, unbalanced parens, unknown functions) produce ParseResult with a specific error message and position.
**Depends:** 1.2.

### Task 1.6: Triple inventory
**Context:** Phase 1's headline deliverable. First value moment of the entire tool.
**Action:** Implement component 02 excluding invariants that require the graph (I6 partial, I7 fully, orphan triples). Implement I1–I5, I8–I10, naming drift detection, completeness matrix, exclusion list generation, trend comparison. Emit findings via the classifier (see next task).
**Verify:** Run all V1–V7 verifications from component 02 spec.
**Depends:** 1.3, 1.4, 1.5, 1.7 (classifier).

### Task 1.7: Finding classifier — skeleton
**Context:** Component 02 wants to emit findings; needs classification. Build the classifier's core now with the rules that apply to Phase 1 detectors.
**Action:** Implement component 11 at ~60% scope: classification pipeline, rules table for detectors 02, 03 (later), 04 (later), summary/detail templating, dedup via store. Skip reclassification and confidence rules requiring grounded modes.
**Verify:** Inject a RawDetection for each signal_type handled by component 02, confirm correct defect_class and layer are assigned. Re-emit an identical detection; deduplication works.
**Depends:** 1.3.

### Task 1.8: Journey graph — BPMN loading and binding
**Context:** Component 02 needs the graph for invariants I6, I7, and orphan detection. Build enough of component 03 to support inventory.
**Action:** Implement component 03 B1, B2, B3, B6, B7. Skip B4, B5 (cross-validation with derived topology) for now — this is Phase 2 polish. Support BPMN 2.0 XML parsing for one or two common node types (task, exclusive_gateway, start, end); defer parallel gateway and intermediate events to Phase 2.
**Verify:** Run V1, V2, V3 from component 03 spec. V4 (loops) and V5 (cross-validation) deferred.
**Depends:** 1.4.

### Task 1.9: Phase 1 wiring and CLI
**Context:** Expose Phase 1 to users. Without a CLI, nobody can actually run it.
**Action:** Implement a CLI: `triple_flow_sim inventory --corpus <bitbucket_url> --bpmn <path> --out reports/`. Wires loader → graph → inventory → classifier → store → minimal report (inventory summary markdown). Report is not the full component 13 — it's a temporary Phase 1 report.
**Verify:** On the test fixture corpus, running the CLI produces a cache directory, a SQLite DB, and a markdown inventory summary. Exit code 0 on success, non-zero on load failures. Findings appear in the DB and match the expected counts.
**Depends:** 1.6, 1.7, 1.8.

### Task 1.10: Phase 1 integration test
**Context:** Phase 1 must deliver value in isolation. An end-to-end test proves it.
**Action:** Create a test corpus with 15-20 triples representing one small journey, with seeded defects (missing intent, missing contracts, orphan obligation, state_flow_gap, regulatory_orphan). Run the CLI end-to-end. Assert expected findings.
**Verify:** All seeded defects are detected with correct defect_class. No unexpected findings. Determinism: two runs produce identical outputs.
**Depends:** 1.9.

**Phase 1 milestone:** Run inventory against a real bitbucket corpus. Hand the resulting markdown report to a SME. That's Phase 1 complete — the team now has a concrete, prioritized authoring backlog without a single LLM call.

---

## Phase 2 — Static Simulation

**Goal:** Catch flow and handoff defects via static contract analysis. Still no LLM. Delivers the second major wave of findings.

**Components:** 04 (full), 03 (finish), plus extensions to 11, 12.

### Task 2.1: Journey graph — complete
**Context:** Phase 1 skipped cross-validation and full node type support. Phase 2 needs them.
**Action:** Implement component 03 B4, B5, parallel gateway support, intermediate events, loop detection with termination analysis. Complete V4, V5 from spec.
**Verify:** Test fixtures exercising loops, parallel splits, and cross-validation disagreements all produce expected findings or structural reports.
**Depends:** 1.8.

### Task 2.2: Expression evaluator — symbolic evaluation
**Context:** Component 04 C3 (predicate satisfiability) and G1 (partition check) require symbolic evaluation over predicate ASTs.
**Action:** Extend the evaluator with `evaluate_symbolic(producer_ast, consumer_ast) -> SymbolicResult`. Support overlap and gap detection for compound predicates. Be conservative — prefer `undetermined` to false positives.
**Verify:** Evaluator correctly identifies overlap (two predicates both true for some input), gap (some input satisfies neither), exhaustive partition (no gaps, no overlaps). Battery of 15+ predicate pair test cases.
**Depends:** 1.5.

### Task 2.3: Static handoff checker — pair checks
**Context:** The core of Phase 2. Pairwise contract compatibility.
**Action:** Implement component 04 B1, B2 (C1–C6), B5 (result emission). Not gateway-specific checks yet — that's next task.
**Verify:** V1, V2, V3 from component 04 spec. Test fixtures: clean pair (no findings), type_mismatch, state_flow_gap, naming_drift, format_mismatch.
**Depends:** 2.1, 2.2, 1.7.

### Task 2.4: Static handoff checker — gateway checks
**Context:** Gateways are where the hardest static analysis lives.
**Action:** Implement component 04 B3 (G1, G2, G3). Extend classifier rules for gateway findings.
**Verify:** V4, V5, V6 from component 04 spec. Test fixtures: gateway with overlapping predicates, gateway with no default, gateway with unparseable predicate.
**Depends:** 2.3.

### Task 2.5: Extend CLI to run static simulation
**Context:** Expose static checking alongside inventory.
**Action:** Add `triple_flow_sim static --corpus ... --bpmn ...` command. Runs inventory then static handoff check. Outputs combined report.
**Verify:** CLI runs both phases in sequence on test corpus, produces findings from both generators, report distinguishes them.
**Depends:** 2.4.

### Task 2.6: Phase 2 integration test
**Context:** Verify the full static pipeline end-to-end.
**Action:** Extend Phase 1 test corpus with handoff-specific defects (type mismatches across edges, orphan obligations with complex closure paths, gateway partition problems). Run static CLI. Assert findings.
**Verify:** All seeded handoff defects detected. No unexpected findings.
**Depends:** 2.5.

**Phase 2 milestone:** Simulator now catches structural defects in the spaces *between* triples. Still zero LLM cost.

---

## Phase 3 — Grounded Simulation

**Goal:** Catch defects that only emerge when an LLM actually executes the triples. Expensive, slow, but highest-signal.

**Components:** 05, 06, 07, 08, plus expansions to 09, 11, 12.

### Task 3.1: LLM client abstraction
**Context:** Components 05-08 all call an LLM. Abstract the interface so model choice is configurable.
**Action:** Implement an `LLMClient` interface with `generate(prompt, max_tokens, temperature, seed) -> LLMResponse`. Concrete Anthropic implementation. Include cost tracking per call, response caching keyed on (prompt_hash, model, temperature, seed), retry logic on transient errors.
**Verify:** A mock LLMClient returns canned responses for tests. The Anthropic client integration passes a smoke test against the real API with a trivial prompt.
**Depends:** 1.1.

### Task 3.2: Prompt templates
**Context:** Grounded components need structured prompts. Hardcoded prompts drift; template files versioned.
**Action:** Create `prompts/` directory with Jinja2 templates for: execute_task, execute_gateway, execute_in_isolation, escalation_detection. Each template includes a version header. Supporting code loads templates and exposes structured output schemas (via tool use or JSON mode).
**Verify:** Templates render correctly on sample inputs. Version is emitted in trace records.
**Depends:** 3.1.

### Task 3.3: Persona generator — canonical and boundary
**Context:** Grounded simulation needs seed contexts. Start with the simplest generators.
**Action:** Implement component 09 B1, B2, B6, B7. Create a persona library with 5-10 canonical personas for a sample journey. Boundary generation from predicate ASTs.
**Verify:** V1, V2, V4, V5 from component 09 spec.
**Depends:** 2.2.

### Task 3.4: Grounded handoff runner
**Context:** First LLM-backed component. Validates the full loop before bigger components.
**Action:** Implement component 05 B1–B5, B7. Skip B6 (repeats) for initial build.
**Verify:** V1–V3 from component 05 spec. Test with mock LLMClient returning scripted responses covering each finding class.
**Depends:** 3.1, 3.2, 3.3.

### Task 3.5: Grounded runner — repeats and confidence
**Context:** LLM non-determinism requires repeat-aware aggregation.
**Action:** Implement component 05 B6. Extend classifier confidence rules (component 11 B4). Extend store to handle confidence updates on dedup.
**Verify:** V4, V5, V6 from component 05 spec. Confidence scores match expected values across mock non-deterministic scenarios.
**Depends:** 3.4.

### Task 3.6: Sequence runner — task execution
**Context:** Full-journey execution. Start with task-only journeys.
**Action:** Implement component 06 B1, B2 (excluding gateways), B3, B5 (partial), B7. No parallel gateway, no regulatory integrity check yet.
**Verify:** V1, V2, V6, V7 from component 06 spec.
**Depends:** 3.5.

### Task 3.7: Sequence runner — gateways and obligations
**Context:** Complete the sequence runner with decision support and obligation tracking.
**Action:** Implement component 06 B2 gateway step, B4 (parallel if in scope), B5 full, B6.
**Verify:** V3, V4, V5 from component 06 spec.
**Depends:** 3.6.

### Task 3.8: Context isolation harness — core
**Context:** The highest-value diagnostic. Build carefully.
**Action:** Implement component 07 B1, B2 (Level 1 — declared_outputs_only), B3, B4, B5. Skip Level 2 and Level 3 for initial build — Level 1 alone is high-signal.
**Verify:** V1, V2, V5 from component 07 spec.
**Depends:** 3.5.

### Task 3.9: Context isolation — calibration mode
**Context:** Harness must be calibrated before findings are trusted at scale.
**Action:** Implement component 07 B6, B7. Create a small calibration set from SME-verified handoffs on the test corpus.
**Verify:** V4 from component 07 spec. Calibration report shows false-positive rate.
**Depends:** 3.8.

### Task 3.10: Context isolation — Levels 2 and 3
**Context:** Extend isolation with additional modes for finer-grained diagnosis.
**Action:** Implement Level 2 (declared + u's content) and Level 3 (full declared state, no undeclared fields). Results table compares all three levels.
**Verify:** V3 from component 07 spec. Diagnosis subtypes correctly distinguished.
**Depends:** 3.9.

### Task 3.11: Branch boundary harness
**Context:** Stress gateway decisions at boundaries.
**Action:** Implement component 08 fully.
**Verify:** V1–V5 from component 08 spec.
**Depends:** 3.7, 3.3.

### Task 3.12: Extend CLI for grounded modes
**Context:** Expose grounded components with budget controls.
**Action:** Add `triple_flow_sim grounded --corpus ... --personas ... --mode [pair|sequence|isolation|boundary]`. Include `--budget-usd` and `--max-tokens` flags. Default to mock LLM for dry runs.
**Verify:** CLI runs each mode end-to-end on test corpus with mock LLM. Budget enforcement works.
**Depends:** 3.11.

### Task 3.13: Phase 3 integration test (static + grounded)
**Context:** Verify grounded pipeline on seeded defects that static alone cannot catch.
**Action:** Extend test corpus with defects requiring grounded detection: triples where declared contract looks fine but content is insufficient, handoffs that only fail under isolation. Run end-to-end with mock LLM scripted to reveal the defects.
**Verify:** Grounded-only defects detected; static defects still detected; isolation-specific finding class appears.
**Depends:** 3.12.

**Phase 3 milestone:** The simulator is feature-complete for detection. Next phase is analysis and ergonomics.

---

## Phase 4 — Generators and Analysis

**Goal:** Complete perturbation/ablation, finish the store, ship the full report suite.

**Components:** 09 (complete), 10, 12 (complete), 13.

### Task 4.1: Persona generator — full
**Context:** Phase 3 built only canonical + boundary. Complete the generator.
**Action:** Implement component 09 B3 (random_valid), B4 (adversarial), B5 (historical). Coverage tracking B6.
**Verify:** V3 from component 09 spec. Coverage metrics report correctly across generated sets.
**Depends:** 3.3.

### Task 4.2: Perturbation generator
**Context:** Stress tests for robustness.
**Action:** Implement component 10 B1, B5, B6 (perturbation side).
**Verify:** V1, V3, V4 from component 10 spec.
**Depends:** 3.7.

### Task 4.3: Ablation generator
**Context:** Blast-radius diagnostics for the corpus.
**Action:** Implement component 10 B2, B3, B4, B6 (ablation side).
**Verify:** V2, V5 from component 10 spec. Ablation sweep on test corpus produces coherent blast-radius table.
**Depends:** 4.2.

### Task 4.4: Finding store — full
**Context:** Phase 1 shipped a skeleton. Complete it.
**Action:** Implement component 12 B4 (blast radius computation), B5 (resolved detection), B7 (lifecycle transitions), B8 (run registration full), B9 (retention). Full query API.
**Verify:** V1–V8 from component 12 spec.
**Depends:** 1.3.

### Task 4.5: Finding classifier — full
**Context:** Phase 1 shipped rules for detectors 02, 03. Phase 3 expanded to 05-08. Finalize and audit.
**Action:** Complete component 11 B3 (severity rules), B5 (full dedup with regression handling), reclassification support. Taxonomy config externalized to YAML.
**Verify:** V5, V6 from component 11 spec. Taxonomy version bump triggers correct reclassification.
**Depends:** 4.4.

### Task 4.6: Report builder — backlog and heatmaps
**Context:** Primary consumption surface for SMEs.
**Action:** Implement component 13 B1, B2, B7, B8. Markdown, JSON, CSV outputs.
**Verify:** V1, V2, V7, V8 from component 13 spec.
**Depends:** 4.5.

### Task 4.7: Report builder — trends, regressions, summary, dossier
**Context:** Complete the report suite.
**Action:** Implement component 13 B3, B4, B5, B6.
**Verify:** V3, V4, V5, V6 from component 13 spec.
**Depends:** 4.6.

### Task 4.8: End-to-end regression harness
**Context:** The simulator itself needs regression protection. Every CI run should verify its own integrity against a known fixture.
**Action:** Create a "golden fixture" corpus + persona set + expected findings JSON. CI test re-runs the full pipeline and diffs findings against golden. Any unexpected change fails CI.
**Verify:** Introduce a deliberate bug (corrupt a finding class rule); CI test fails with a clear diff.
**Depends:** 4.7.

### Task 4.9: Documentation
**Context:** The tool's value is gated on people using it. Docs gate usage.
**Action:** Write: README.md with quickstart, architecture.md covering the 13 components, taxonomy.md explaining defect classes with examples, authoring-guide.md advising SMEs on writing triples that simulate cleanly, operations.md on running in CI/scheduled modes.
**Verify:** A fresh engineer can follow quickstart and run the tool against the test corpus within 30 minutes. SME can read taxonomy.md and correctly classify 10 sample findings.
**Depends:** 4.8.

**Phase 4 milestone:** Production-ready tool. Deployed in CI. Findings driving the authoring backlog weekly.

---

## Cross-phase discipline

Throughout all phases:

1. **Every task ends with inline verification.** No task is "done" until the Verify step passes.
2. **Every component gets unit tests alongside implementation.** Tests live in `tests/unit/<component_number>/`. Integration tests in `tests/integration/`.
3. **Every finding emission gets traced.** The trace records are themselves evidence for the simulator's correctness.
4. **Config is externalized.** No magic numbers or hardcoded strings. YAML config with schema validation.
5. **LLM budget is instrumented from day one.** Every grounded call records cost. Weekly cost reports per run.
6. **Taxonomy versions are bumped on any defect_class change.** Migration logic ships with the change.
7. **Every component has a spec reference in its module docstring.** A maintainer opens the code and sees which spec file to read for full context.

---

## Effort and timeline estimate

Rough order-of-magnitude effort in engineer-days, assuming one focused engineer with Claude Code:

- Phase 1: ~5 days. Delivers inventory report. **First value within week 1.**
- Phase 2: ~4 days. Delivers static handoff detection.
- Phase 3: ~12 days. The heavy lift. Includes careful calibration of component 07.
- Phase 4: ~6 days. Polish and ergonomics.

Total: ~27 engineer-days for v1. Halvable with multiple engineers if tasks are partitioned along component boundaries, which the decomposition supports.

Ship Phase 1 on day 5 regardless of Phase 2+ timeline. The inventory report is genuinely valuable standalone and establishes the tool's credibility before the larger investment.
