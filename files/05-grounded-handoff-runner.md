# Component 05 — Grounded Handoff Runner

## Purpose

For a single (u, v) pair, execute triple u with an LLM against a seed context, capture what it actually produces, then attempt to execute triple v with that output. Detects defects that static checks miss: contracts look compatible on paper but the real produced output doesn't flow cleanly into the consumer.

## Inputs

- A pair `(u, v)` from the journey graph.
- A seed context for triple u (provided by persona generator, component 09).
- LLM configuration: model, temperature, seed, prompt template.

## Outputs

- `TraceStep` for u and v each, with `llm_interaction` populated.
- `Findings` with `generator=grounded_pair`.
- Repeat-aware aggregation: if run N times, outcomes are summarized as modal outcome + variance.

## Behavior

### B1. Execute triple u

Construct a prompt containing:
- `u.cim.intent`
- `u.psm.enriched_content` (all chunks)
- `u.psm.prompt_scaffold` if present
- The seed context (filtered to `u.pim.state_reads` in strict mode; full context in permissive mode — this is configurable per run)
- Instructions requesting the LLM to:
  - Describe what it will do
  - Produce the declared postconditions as structured output
  - Open/close obligations as appropriate
  - If a gateway: choose an edge and cite the evidence

Call LLM. Parse response according to an output schema (JSON, with fallback to structured text parsing).

### B2. Capture observed outputs

From the LLM response:
- `observed_writes` — state paths actually written, with values.
- `observed_reads` — if the LLM response cites specific context fields, record them.
- `branch_taken` — for gateway nodes, which edge was chosen.
- `evidence_cited` — chunks the LLM referenced.
- `refusal` — if the LLM declined to proceed (e.g., "insufficient information to determine X").

### B3. Contract observation checks

Compare observed against declared:

- **Undeclared writes:** observed_writes contains paths not in `u.pim.state_writes` → `output_under_declaration` finding.
- **Missing expected outputs:** declared writes not present in observed → `output_over_promise` finding.
- **Undeclared reads:** if LLM response references context fields not in `u.pim.state_reads` → `input_under_declaration`. This is a weaker signal here; the stronger version is in component 07.
- **Refusal as finding:** refusal with a reason implicating missing information → `content_missing` at PSM with the refusal reason captured.

### B4. Execute triple v with u's output

Apply u's observed writes to the seed context, producing an updated context. Now execute v:
- Prompt contains v's content and the updated context.
- Parse v's response.

Check:
- **Handoff format mismatch:** v's response suggests it misinterpreted u's output (e.g., treated a structured value as text, or couldn't parse a timestamp). → `handoff_format_mismatch`.
- **Escalation/confusion:** v refuses with a reason like "upstream output unclear" → strong signal for handoff defect.
- **Silent inference:** v proceeds but its output implies it filled a gap (e.g., u didn't produce `borrower.consent_method` but v's output assumes email consent). → `handoff_implicit_setup`. Detection heuristic: v writes paths derivable only from information not present in the context.

### B5. Branch choice verification (if u is a gateway)

If u is a gateway:
- Run static predicate evaluation on the context using component 04's concrete evaluator.
- Compare with the LLM's chosen branch.
- Mismatch → `branch_misdirection` finding.
- If the LLM's branch choice is consistent but the LLM's cited evidence doesn't match the chunks declared in that branch's `evidence_refs` → observation for SME review (not a finding, but logged).

### B6. Repeat handling

Configurable N (default 5). Run the pair N times with the same seed.
- If all N runs produce identical observed_writes and identical branch choices: confidence = high.
- If > 50% agree: confidence = medium; report modal outcome and variance.
- If < 50% agree: confidence = low; emit `nondeterminism` observation.

Findings from individual repeats are deduplicated and confidence-stamped.

### B7. Budget control

Per-run token budget and per-session cost ceiling. Configuration:
- `max_tokens_per_pair` (default 8000)
- `max_repeats` (default 5)
- `max_cost_per_session_usd` (default configurable; aborts with a warning if exceeded)

When budget exhausts, remaining pairs are skipped with note in report.

## Public API

```python
class GroundedHandoffRunner:
    def __init__(self, graph: JourneyGraph, llm: LLMClient, config: RunnerConfig): ...
    def run_pair(self, u: str, v: str, seed_context: JourneyContext, repeats: int = 5) -> list[TraceStep]: ...
    def run_all_pairs(self, seed_contexts: list[JourneyContext]) -> GroundedReport: ...
```

## What this component does NOT do

- Does not execute full journeys — single pair only. Full journeys are component 06.
- Does not construct seed contexts — receives them from persona generator.
- Does not repair any defects.
- Does not make budget decisions silently — abort is explicit and logged.

## Dependencies

- Component 03 (Journey Graph).
- Component 04 (expression evaluator for branch verification).
- Component 09 (Persona Generator) for seed contexts.
- LLM client (Anthropic API or compatible).
- Prompt template file (versioned).
- `contracts/trace-schema.md`, `contracts/finding-schema.md`.
- Component 12 (Finding Store).

## Verification

**V1.** A well-formed pair where u writes exactly its declared postconditions produces zero findings across 5 repeats.

**V2.** A pair where u's content subtly lacks information for its declared postcondition produces `content_missing` or `output_over_promise` findings with medium-to-high confidence.

**V3.** A pair where u writes a timestamp and v expects a business-day-adjusted date produces `handoff_format_mismatch`.

**V4.** A gateway whose content doesn't clearly distinguish its branches produces either `branch_misdirection` (on disagreement with static eval) or `nondeterminism` (on variance across repeats).

**V5.** A pair where v proceeds successfully but writes a path not implied by its inputs produces `handoff_implicit_setup`.

**V6.** Budget exhaustion is handled gracefully: remaining pairs skipped, report notes the budget cap.

## Implementation notes

- Prompt template versioning is critical — include the version in every trace. Template changes invalidate prior traces for regression comparison.
- Parse LLM output with a tolerant JSON parser; fall back to structured text extraction with explicit labels ("WRITES:", "READS:", "BRANCH:").
- Use Anthropic's tool-use / structured output features where available to force schema adherence.
- Log full prompts and responses to traces; they're evidence for findings.
- For expensive models, cache responses keyed on (triple_id, triple_version, context_hash, prompt_template_version, temperature, seed). Cache hits skip the API call.
- Keep refusal detection robust — the LLM may express "I can't do this because..." in various ways; treat any response that doesn't fill the required output schema as a refusal and capture the free-text reason.
