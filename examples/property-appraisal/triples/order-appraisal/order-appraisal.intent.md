---
intent_id: "INT-PA-ORD-001"
intent_name: "Submit Appraisal Order to AMC"
bpmn_task_id: "Task_OrderAppraisal"
bpmn_task_name: "Order Appraisal"
process_id: "Process_PropertyAppraisal"
process_name: "Property Appraisal"
goal: "Submit appraisal order to AMC with property details and assignment requirements"
goal_type: "notification"

version: "1.0.0"
status: "draft"

generated_from: "CAP-PA-ORD-001"
generated_date: "2026-04-09"
generated_by: "mda-pipeline"
last_modified: "2026-04-09"
last_modified_by: "mda-pipeline"

owner_role: "Solution Architect"
owner_team: "Mortgage Technology"
reviewers:
  - "Appraisal Desk Supervisor"
  - "Integration Architect"

domain: "Mortgage"
subdomain: "Property Appraisal"
mda_layer: "PIM"

agent_type: "rpa"
autonomy_level: "supervised"
confidence_threshold: 0.98
timeout_seconds: 120
retry_policy: "exponential-backoff"
max_retries: 3

capsule_id: "CAP-PA-ORD-001"
contract_id: "ICT-PA-ORD-001"
contract_ref: "ICT-PA-ORD-001"
predecessor_ids: []
successor_ids:
  - "INT-PA-RCV-001"

preconditions:
  - "Loan application exists in the LOS with status Approved-for-Appraisal or equivalent."
  - "Property address has been validated and geocoded."
  - "Borrower appraisal fee authorization is on file and payment method is valid."
  - "At least one approved AMC with geographic coverage for the property location is available."
postconditions:
  - "An appraisal order has been transmitted to exactly one AMC via the Appraisal Portal."
  - "The LOS contains the order confirmation number, AMC name, and estimated completion date."
  - "The appraisal fee has been charged or reserved against the borrower's authorization."
  - "Loan status has been updated to Appraisal Ordered with a timestamp."
invariants:
  - "The loan officer who originated the loan has no direct contact with the appraiser or AMC."
  - "No appraisal order data is modified after transmission without a new revision record."
success_criteria:
  - "Order transmitted and confirmation received from AMC within 60 seconds."
  - "All required fields in the MISMO XML order payload are populated."

execution_hints:
  preferred_agent: "property-appraisal-agent"
  tool_access: []
  forbidden_actions:
    - "browser_automation"
    - "screen_scraping"
    - "ui_click"
    - "rpa_style_macros"

gaps:
  - "Desktop appraisal eligibility logic not yet specified -- Product team to define"
---

# Submit Appraisal Order to AMC

## Outcome Statement

When this intent is fulfilled, a valid appraisal order has been placed with a qualified AMC, the loan file reflects the order status, and the appraisal fee has been collected. The agent achieves this by assembling order data from the LOS, selecting an AMC per rotation policy, and transmitting a MISMO-compliant order payload while respecting appraiser independence requirements.

## Outcome Contract

**Preconditions (GIVEN):**

- A loan application exists in the LOS with a status indicating readiness for appraisal ordering.
- The property address has been validated and geocoded to confirm AMC coverage.
- The borrower has authorized payment of the appraisal fee.
- At least one AMC in the approved panel covers the property's geographic area.

**Postconditions (THEN):**

- Exactly one appraisal order has been transmitted to one AMC.
- The LOS has been updated with order confirmation details.
- The appraisal fee charge has been initiated.
- The loan workflow status reflects the order placement.

**Invariants (ALWAYS):**

- Appraiser independence is maintained throughout the ordering process.
- Order data is immutable after transmission.

## Reasoning Guidance

1. **Assess inputs** -- Validate that the loan file contains all required property details (address, type, legal description) and that fee authorization is active.
2. **Determine appraisal form type** -- Based on loan program (conventional, FHA, VA) and property type, select the correct URAR form (1004, 1073, 1025, 2055).
3. **Select AMC** -- Query the vendor management system for the next AMC in the rotation queue with coverage for the property's county and state.
4. **Assemble order payload** -- Build the MISMO XML order with property details, loan parameters, form type, and any special instructions.
5. **Transmit order** -- Send the order via the Appraisal Portal API and capture the confirmation response.
6. **Update LOS** -- Write the order confirmation, AMC assignment, and estimated turnaround to the loan file.
7. **Validate postconditions** -- Confirm that exactly one order exists, the fee was charged, and the loan status was updated.

## Anti-Patterns

The agent MUST NOT:

- **Generate, suggest, or assume any user-interface element** -- no HTML, no CSS, no screen layouts, no form designs, no UI framework references.
- **Produce wireframes, mockups, or visual design artifacts** -- presentation is a downstream concern outside the triple.
- **Reference specific frontend technologies** (React, Angular, SwiftUI, etc.) in its reasoning or output.
- **Modify, delete, or fabricate input data** -- the agent operates on data as-received; any corrections must be flagged, not silently applied.
- **Exceed its autonomy level** -- if `autonomy_level` requires human confirmation, the agent must pause and request it.
- **Ignore confidence thresholds** -- results below `confidence_threshold` must be escalated, never silently committed.
- **Select an appraiser directly** -- all appraiser assignment must flow through the AMC to maintain independence.
- **Bypass the AMC rotation policy** -- favoritism or repeated assignment to the same AMC must be prevented.
- **Transmit borrower financial data to the appraiser** -- only property and engagement details are included in the order.

## Paired Capsule

| Field | Value |
|-------|-------|
| Capsule ID | `CAP-PA-ORD-001` |
| Capsule Name | Order Appraisal |
| Location | `triples/order-appraisal/order-appraisal.cap.md` |

## Paired Integration Contract

| Field | Value |
|-------|-------|
| Contract ID | `ICT-PA-ORD-001` |
| Contract Name | Order Appraisal Binding |
| Location | `triples/order-appraisal/order-appraisal.contract.md` |
