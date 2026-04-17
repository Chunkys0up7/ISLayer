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

## Demo UI

A Streamlit UI bundles the four phases behind one browser tab — pick a corpus, click Run, browse the journey graph, findings, and the Context Isolation walkthrough side-by-side.

```bash
pip install -e ".[ui]"
streamlit run triple_flow_sim/ui/streamlit_app.py
```

Then open http://localhost:8501. The sidebar ships with two pre-loaded demo corpora (`corpus_clean` and `corpus_seeded`), or upload your own loader.yaml + BPMN pair. Default driver is the deterministic `fake` LLM so the demo runs offline in under a second. Switch to `auto` or `anthropic` once `ANTHROPIC_API_KEY` is set and the `anthropic` package is installed.

The UI has four tabs:
- **🗺 Journey graph** — interactive BPMN via pyvis, color-coded by binding + finding severity.
- **📋 Findings** — filterable table by severity and defect class.
- **🔬 Isolation walkthrough** — the keystone diagnostic. Pick a triple, see Level 1 / Level 2 / Level 3 prompts + responses side-by-side, with the divergence signature flagged when the contract is riding on undeclared context.
- **📝 Grounded trace** — per-persona sequence run with each step's declared vs observed writes.

## Spec references

Specifications live in `../files/`. See `../files/README.md` for the spec package overview.
Implementation plan: `../TRIPLE-FLOW-SIM-PHASE1-SPEC.md` (once generated).

## License

MIT — see `../LICENSE`.
