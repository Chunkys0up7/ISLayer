# Triple Review Guide

This guide is for process analysts, tech leads, and compliance reviewers who review triples in pull requests. A triple is the unit of work in the MDA Intent Layer: a capsule, an intent spec, and an integration contract that together describe one BPMN task completely.

## What You Are Reviewing

Every BPMN task produces a triple -- three artifacts that work together:

1. **Capsule** (`.cap.md`) -- The human-readable description of what happens at this task. Contains the procedure, business rules, inputs, outputs, and exception handling. This is the "what" and "how."

2. **Intent Spec** (`.intent.md`) -- The agent-executable specification. Contains the goal, preconditions, invariants, success criteria, failure modes, and execution constraints. This is the "contract with the agent."

3. **Contract** (`.contract.md`) -- The integration binding. Contains the actual API endpoints, protocols, authentication methods, SLAs, and audit configuration. This is the "how it connects to real systems."

All three artifacts must be reviewed as a unit. A capsule with a correct procedure but an intent spec with missing invariants is an incomplete triple. A contract that binds to the wrong API renders the whole triple unusable.

## Review Checklist by Role

### Process Owner

Your job is to verify that the capsule accurately reflects how the business process actually works.

- [ ] Does the procedure match your current SOP?
- [ ] Are all steps present and in the correct order?
- [ ] Are the business rules correct and from authoritative sources?
- [ ] Are the inputs and outputs complete?
- [ ] Do the exception handling paths cover real-world scenarios?
- [ ] Are the regulatory citations accurate and current?
- [ ] Are there gaps that need to be resolved before this triple can be used?

### Tech Lead

Your job is to verify that the intent spec is technically sound and that an agent could execute it correctly.

- [ ] Does the goal clearly state what the task accomplishes?
- [ ] Are preconditions observable and testable (not assumed)?
- [ ] Are invariants expressed as MUST/MUST NOT constraints?
- [ ] Are failure modes realistic and do the detection/action pairs make sense?
- [ ] Are forbidden_actions present (no browser automation, screen scraping, or UI interaction)?
- [ ] Is the timeout reasonable for the work being done?
- [ ] Is the retry policy appropriate?
- [ ] Are side_effects documented?

### Integration Lead

Your job is to verify that the contract binds to real, accessible systems with correct details.

- [ ] Are the API endpoints correct (or clearly marked as unbound)?
- [ ] Is the binding_status accurate (`bound`, `unbound`, or `partial`)?
- [ ] Is the authentication method correct for each source and sink?
- [ ] Are SLAs reasonable for the actual system capabilities?
- [ ] Are the schema references pointing to real schemas?
- [ ] Is the audit configuration complete (record type, retention, required fields)?
- [ ] Are unbound sources/sinks documented with clear explanation of what is missing?

### Compliance

Your job is to verify regulatory accuracy and audit completeness.

- [ ] Do the regulation_refs in the capsule cite the correct regulatory sections?
- [ ] Are policy_refs current (not superseded policies)?
- [ ] Is the audit retention period correct for this type of activity?
- [ ] Are all required audit fields captured (borrower ID, loan ID, timestamp, agent ID)?
- [ ] Does the procedure enforce required timing (e.g., TRID deadlines)?
- [ ] Are fair lending and consumer protection requirements addressed?

## Using mda validate

Before reviewing the content, run structural validation to catch schema and consistency issues:

```bash
mda validate
```

This checks all triples in the `triples/` and `decisions/` directories against the JSON schemas. It catches:

- Missing required frontmatter fields
- Invalid field values (wrong enum, wrong type)
- Broken cross-references (capsule references an intent that does not exist)
- Predecessor/successor mismatches (A says B follows, but B does not say A precedes)

You can also validate a single triple directory:

```bash
mda validate triples/verify-w2/
```

Or set a severity threshold for CI pipeline failures:

```bash
mda validate --fail-on medium
```

**Always run `mda validate` before starting a manual review.** Fix structural issues first so you can focus your review time on content quality.

## Using mda review

For LLM-assisted quality review, use the review command:

```bash
mda review triples/verify-w2/
```

This sends the triple to an LLM that evaluates it for completeness, consistency, and quality. The output includes an overall rating and specific findings:

```
Review: verify-w2
  Overall: PASS (with warnings)

  Findings (3)
  Severity  Aspect       File                 Finding
  low       completeness verify-w2.cap.md     OCR confidence threshold not specified
  low       consistency  verify-w2.intent.md  Timeout of 180s may be tight for IVES calls
  medium    binding      verify-w2.contract.md IVES endpoint marked optional but no fallback

  Recommendations:
    [medium] Define explicit fallback when IVES is unavailable
```

You can focus the review on a specific aspect:

```bash
mda review triples/verify-w2/ --aspect compliance
```

Or save the review output for the PR:

```bash
mda review triples/verify-w2/ --output review-results.json
```

## What to Look For in Each Artifact

### Capsule Review

The capsule is the human-readable part. Focus on accuracy and completeness.

**Procedure completeness**: Walk through the procedure steps mentally. Can you follow them from start to finish without guessing? Are there decision points where you would not know what to do?

For example, in the W-2 verification capsule, the procedure includes specific steps for collecting documents, classifying employment, calculating base income (with formulas for hourly vs. salaried), performing trending analysis, verifying employment, and reconciling the final income figure. Each step has enough detail that a person or agent could execute it.

**Business rules from authoritative sources**: Every business rule should cite its source. Check that the citation is correct and current.

```markdown
## Business Rules

- Fannie Mae Selling Guide B3-3.1-01: Salary and wage income must be
  verified with W-2s and pay stubs covering the most recent 30 days
  plus the most recent two years.
```

If a rule cites "Fannie Mae Selling Guide B3-3.1-09" but the actual guidance is in B3-3.1-01, flag it.

**Gaps documented**: Gaps are places where information is missing or uncertain. They appear in the capsule frontmatter:

```yaml
gaps:
  - type: "missing_detail"
    description: "OCR extraction confidence threshold not yet defined"
    severity: "low"
```

Review whether the gap severity is appropriate. A missing confidence threshold is low severity. A missing procedure for an entire income type would be high or critical.

**Inputs and outputs**: Verify that every piece of data the procedure needs is listed as an input, and every result it produces is listed as an output. Missing inputs mean the agent will not have the data it needs. Missing outputs mean downstream tasks will not receive what they expect.

### Intent Spec Review

The intent spec is the agent-executable part. Focus on precision and safety.

**Goal matches the BPMN task**: The goal statement should describe exactly what this task accomplishes, not more and not less. Compare it to the BPMN task name and the capsule purpose.

```yaml
goal: "Verify the borrower's W-2 wage income by cross-referencing
       W-2 forms against IRS tax return transcripts and computing
       a reliable monthly income figure for qualifying income
       calculation."
```

**Preconditions are observable**: Every precondition should be something the agent can check before starting. Avoid vague preconditions.

```yaml
# Good - observable and testable
preconditions:
  - "W-2 documents for the most recent 2 tax years are available
     in DocVault with status AVAILABLE or VERIFIED."

# Bad - how does the agent check this?
preconditions:
  - "The borrower has provided all necessary documentation."
```

**Invariants are MUST/MUST NOT constraints**: Invariants define what must always be true during and after execution. They should be precise enough to test.

```yaml
invariants:
  - "W-2 Box 1 totals MUST NOT exceed 1040 Line 1 for the same
     tax year."
  - "If income declined year-over-year by more than 10%, the
     verified income MUST use the lower year or the 2-year average,
     whichever is less."
```

Watch for invariants that are too vague ("income must be reasonable") or too narrow (hard-coding a specific dollar threshold that should come from configuration).

**Forbidden actions are present**: Every intent spec must include the anti-UI principle. Check that `forbidden_actions` includes:

```yaml
forbidden_actions:
  - "browser_automation"
  - "screen_scraping"
  - "ui_click"
  - "rpa_style_macros"
```

**Failure modes have detection and action**: Each failure mode needs both a way to detect it and an action to take. The action should be specific.

```yaml
failure_modes:
  - mode: "W-2 document parse failure"
    detection: "Structured data extraction failed or confidence below threshold"
    action: "Re-queue for manual extraction; flag for underwriter"
```

If a failure mode says "action: handle appropriately," that is too vague. What does the agent actually do?

### Contract Review

The contract is the integration binding. Focus on accuracy and completeness.

**Endpoints are real or clearly unbound**: Check that API endpoints point to actual systems. If the endpoint is a placeholder, the binding_status should reflect that.

```yaml
binding_status: "unbound"
unbound_sources:
  - "IVES integration is optional; many lenders rely on borrower-provided
     transcripts uploaded to DocVault"
```

A contract with `binding_status: "bound"` but placeholder URLs (`https://example.com/api/...`) is wrong. It should be `unbound` or `partial`.

**SLAs are reasonable**: Check that SLA values match the actual system capabilities. A 5,000 ms SLA for a database lookup is generous. A 5,000 ms SLA for an IRS transcript request is unrealistic (the IVES example correctly uses 30,000 ms).

**Audit is configured**: Every contract should have an audit section with:
- `record_type`: What kind of audit record this creates
- `retention_years`: How long to keep it (typically 7 years for mortgage lending)
- `fields_required`: What data must be captured in the audit record
- `sink`: Where audit records are sent

## Cross-Reference Verification

Verify that IDs match across the triple:

| Check | Where to Look |
|-------|---------------|
| Capsule references the correct intent | `capsule.intent_id` matches `intent.intent_id` |
| Capsule references the correct contract | `capsule.contract_id` matches `contract.contract_id` |
| Intent references the correct capsule | `intent.capsule_id` matches `capsule.capsule_id` |
| Intent references the correct contract | `intent.contract_ref` matches `contract.contract_id` |
| Contract references the correct intent | `contract.intent_id` matches `intent.intent_id` |
| Predecessor flow is correct | `capsule.predecessor_ids` lists the correct upstream capsules |
| Successor flow is correct | `capsule.successor_ids` lists the correct downstream capsules |

Also verify that predecessor/successor relationships are bidirectional. If capsule A lists capsule B as a successor, capsule B should list capsule A as a predecessor. The `mda validate` command checks this automatically, but it is worth confirming during review.

## Gap Triage

Gaps are a normal part of the generation process. Not every gap needs to be resolved before merging.

**When to accept a triple with gaps:**

- The gap is `low` severity and does not affect the core procedure (e.g., an OCR confidence threshold that can be configured later)
- The gap is documented with enough detail that someone can resolve it later
- The gap does not create a safety or compliance risk
- The triple is otherwise complete and accurate

**When to require gap resolution before merge:**

- The gap is `critical` or `high` severity
- The gap affects a compliance requirement (e.g., missing regulatory citation for a required step)
- The gap means the agent cannot complete the task (e.g., missing input data source)
- The gap affects audit trail completeness

You can see all gaps across the project:

```bash
mda gaps
```

Or filter by severity:

```bash
mda gaps --severity critical
```

## Anti-UI Principle Verification

The MDA Intent Layer is built on a core principle: agents interact with systems through APIs and data, never through user interfaces. During review, verify that no artifact contains any of the following:

- References to clicking buttons, navigating screens, or filling forms
- Browser automation instructions (Selenium, Puppeteer, Playwright)
- Screen scraping or DOM parsing
- RPA-style macro steps
- References to specific UI elements (dropdown menus, checkboxes, text fields)
- Instructions to "log in to the system" or "open the application"

The intent spec should have `forbidden_actions` that explicitly prohibit these patterns. If you find UI-style instructions in the capsule procedure, flag them -- the procedure should describe the business logic, not how to operate a user interface.

**Wrong** (UI-style):
```
1. Log in to the LOS
2. Navigate to the Income tab
3. Click "Add Income Source"
4. Enter the W-2 Box 1 amount in the "Annual Income" field
```

**Right** (API-style):
```
1. Retrieve the borrower's income record from the LOS via
   GET /loans/{loanId}/borrowers/{borrowerId}
2. Extract W-2 Box 1 amount from the structured document data
3. Update the income source via PATCH with the verified amount
```

## PR Workflow

### Branch strategy

Create a feature branch for each set of related changes:

```bash
git checkout -b feat/verify-w2-triple
```

Use descriptive branch names that indicate what triples are being added or changed.

### What to include in the PR

- All three files of each triple (capsule, intent, contract)
- The triple manifest (`triple.manifest.json`) if updated
- Any new or updated corpus documents that feed the triples
- Any new or resolved gap files

### Commit messages

Be specific about what changed:

```
Add verify-w2 triple for income verification process

- Capsule: W-2 verification procedure with 7-step process
- Intent: Computation goal with W-2/1040 cross-reference invariants
- Contract: DocVault and IVES bindings (IVES unbound/optional)
- Gap: OCR confidence threshold TBD (low severity)
```

### Merge requirements

Before merging a triple PR:

1. `mda validate` passes with no critical or high errors
2. At least one process owner has reviewed the capsule
3. At least one tech lead has reviewed the intent spec
4. Integration lead has reviewed the contract (if binding_status is `bound`)
5. Compliance has reviewed regulation_refs and audit configuration
6. All critical and high severity gaps have been resolved or have an accepted plan

## Common Review Findings and How to Fix Them

| Finding | How to Fix |
|---------|-----------|
| Capsule procedure is too vague ("verify the income") | Add specific numbered steps with concrete actions and decision criteria |
| Intent precondition is not observable | Rewrite as something the agent can check (data exists, status equals X) |
| Intent is missing invariants | Extract MUST/MUST NOT rules from the capsule business rules section |
| Intent has no forbidden_actions | Add the standard anti-UI block (browser_automation, screen_scraping, ui_click, rpa_style_macros) |
| Contract has placeholder URLs but binding_status is "bound" | Change binding_status to "unbound" and document what is needed in unbound_sources |
| Contract is missing audit configuration | Add audit section with record_type, retention_years, fields_required, and sink |
| Predecessor/successor IDs do not match | Verify the BPMN sequence flow and update both the predecessor and successor capsules |
| Regulation ref cites wrong section | Look up the correct section in the regulation corpus document and update |
| Gap marked "low" but blocks agent execution | Raise the severity to "high" or "critical" |
| Capsule has UI-style instructions | Rewrite to describe business logic and API interactions, not screen navigation |
