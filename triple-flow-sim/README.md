# Triple Flow Simulator

A diagnostic simulator for inter-triple handoffs in the MDA Intent Layer.

## What it does

Given a corpus of CIM→PIM→PSM triples (one per BPMN step or decision), this tool tests:

1. **Contract completeness** — do triples declare their inputs, outputs, and obligations?
2. **Structural integrity** — does the BPMN graph resolve cleanly against the triple set?
3. **Static handoff conformance** (Phase 2) — do producer outputs satisfy consumer inputs?
4. **Grounded handoff conformance** (Phase 3) — does an LLM agent actually complete handoffs?
5. **Context isolation** (Phase 3) — do handoffs succeed only with declared context, not undeclared ambient context?

Every run produces a **finding set** classified by a formal taxonomy. The output is a ranked defect backlog, not a pass rate.

## What it is NOT

- Not a triple generator — that's the main MDA Intent Layer CLI.
- Not a content validator — it tests handoffs, not knowledge accuracy.
- Not a production runtime — offline diagnostic against static triple snapshots.

## Phase 1 (current)

Foundation: ingest triples, produce an inventory and completeness report. Zero LLM calls. First value delivery.

Supports two triple formats:
- **Native** — YAML/JSON conforming to `files/triple-schema.md` verbatim
- **MDA** — the current per-file format used in `../examples/` (capsule + intent + contract + optional jobaid)

## Quick start

```bash
# From the triple-flow-sim/ directory
pip install -e .

# Run inventory on an existing MDA process
python -m triple_flow_sim inventory \
  --corpus-config config/mda-income-verification.yaml \
  --bpmn ../examples/income-verification/bpmn/income-verification.bpmn \
  --out ./reports

# Results:
#   ./reports/<run_id>/inventory.md   — human-readable report
#   ./reports/<run_id>/inventory.json — machine-readable report
#   ./reports/<run_id>/findings.db    — SQLite findings store
```

## Spec references

Specifications live in `../files/`. See `../files/README.md` for the spec package overview.
Implementation plan: `../TRIPLE-FLOW-SIM-PHASE1-SPEC.md` (once generated).

## License

MIT — see `../LICENSE`.
