---
intent_id: "INT-PA-ASV-001"
intent_name: "Calculate LTV and Assess Collateral Adequacy"
bpmn_task_id: "Task_AssessValue"
bpmn_task_name: "Assess Property Value"
process_id: "Process_PropertyAppraisal"
process_name: "Property Appraisal"

version: "1.0.0"
status: "draft"

generated_from: "CAP-PA-ASV-001"
generated_date: "2026-04-09"
generated_by: "mda-pipeline"
last_modified: "2026-04-09"
last_modified_by: "mda-pipeline"

owner_role: "Solution Architect"
owner_team: "Mortgage Technology"
reviewers:
  - "Chief Appraiser"
  - "Risk Officer"

domain: "Mortgage"
subdomain: "Property Appraisal"
mda_layer: "PIM"

agent_type: "hybrid"
autonomy_level: "supervised"
confidence_threshold: 0.95
timeout_seconds: 300
retry_policy: "fixed-delay"
max_retries: 2

capsule_id: "CAP-PA-ASV-001"
contract_id: "ICT-PA-ASV-001"
contract_ref: "ICT-PA-ASV-001"
goal: "Calculate LTV ratio and determine collateral adequacy based on appraised value and loan parameters"
goal_type: "data_production"
predecessor_ids:
  - "INT-PA-VAL-001"
successor_ids:
  - "INT-PA-NTF-001"
  - "INT-PA-MRV-001"

preconditions:
  - "The appraisal report has passed the completeness validation."
  - "The appraised value and comparable sales data are available in the UAD XML."
  - "The loan amount and transaction type are recorded in the LOS."
postconditions:
  - "The LTV ratio has been calculated and recorded in the LOS."
  - "An LTV determination (Within LTV or Exceeds LTV) has been made."
  - "Any adjustment reasonableness flags or market condition flags are recorded."
invariants:
  - "The appraised value from the report is never modified by the assessment."
  - "LTV is always calculated using the lesser of appraised value or purchase price for purchase transactions."
success_criteria:
  - "LTV calculation accuracy matches manual calculation in 100% of cases."
  - "All adjustment threshold violations are detected and flagged."

execution_hints:
  preferred_agent: "property-appraisal-agent"
  tool_access: []
  forbidden_actions:
    - "browser_automation"
    - "screen_scraping"
    - "ui_click"
    - "rpa_style_macros"

gaps:
  - "AVM integration for cross-validation not yet available -- Vendor evaluation in progress"
---

# Calculate LTV and Assess Collateral Adequacy

## Outcome Statement

When this intent is fulfilled, the LTV ratio has been calculated, comparable sales adjustments have been evaluated for reasonableness, and a routing decision has been made based on whether the property value supports the requested financing. The agent achieves this by combining structured UAD data with loan parameters and applying GSE adjustment thresholds.

## Outcome Contract

**Preconditions (GIVEN):**

- A validated appraisal report with appraised value and comparable sales exists.
- Loan amount and transaction type are available in the LOS.

**Postconditions (THEN):**

- LTV ratio is calculated and stored.
- LTV determination routes the workflow appropriately.
- Adjustment and market condition flags are recorded.

**Invariants (ALWAYS):**

- The appraised value is used as-reported, never modified.
- For purchases, LTV uses the lesser of appraised value or purchase price.

## Reasoning Guidance

1. **Assess inputs** -- Retrieve appraised value, comparable sales, loan amount, purchase price, and transaction type.
2. **Verify comparable sales** -- Cross-reference reported comparables against available market data if MLS API is accessible.
3. **Evaluate adjustments** -- Check net and gross adjustments against 15%/25% thresholds for each comparable.
4. **Calculate LTV** -- Apply the correct formula based on transaction type (purchase vs. refinance).
5. **Compare against program limits** -- Determine if the LTV is within the maximum allowed by the loan program.
6. **Flag risk indicators** -- Note declining markets, value inflation, or excessive adjustments.
7. **Compose output** -- Build the assessment summary with LTV, flags, and routing decision.
8. **Validate postconditions** -- Confirm the LTV is recorded and the routing decision is set.

## Anti-Patterns

The agent MUST NOT:

- **Generate, suggest, or assume any user-interface element** -- no HTML, CSS, or UI references.
- **Modify the appraised value** -- the agent assesses but never changes the appraiser's conclusion.
- **Override LTV thresholds** -- program maximums are hard limits that cannot be waived by the agent.
- **Ignore adjustment flags** -- threshold violations must always be recorded even if LTV is within limits.
- **Use AVM as a replacement for the appraisal** -- AVM data is supplementary only.
- **Approve loans with impossible LTV calculations** -- data integrity errors must halt processing.

## Paired Capsule

| Field | Value |
|-------|-------|
| Capsule ID | `CAP-PA-ASV-001` |
| Capsule Name | Assess Property Value |
| Location | `triples/assess-value/assess-value.cap.md` |

## Paired Integration Contract

| Field | Value |
|-------|-------|
| Contract ID | `ICT-PA-ASV-001` |
| Contract Name | Assess Property Value Binding |
| Location | `triples/assess-value/assess-value.contract.md` |
