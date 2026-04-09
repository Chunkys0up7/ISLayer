---
intent_id: "INT-PA-NTF-001"
intent_name: "Publish Appraisal Completion Event"
bpmn_task_id: "Task_EmitComplete"
bpmn_task_name: "Emit Appraisal Complete Event"
process_id: "Process_PropertyAppraisal"
process_name: "Property Appraisal"

goal: "Publish appraisal completion event to notify downstream systems that appraisal review is finalized"
goal_type: "notification"

version: "1.0.0"
status: "draft"

generated_from: "CAP-PA-NTF-001"
generated_date: "2026-04-09"
generated_by: "mda-pipeline"
last_modified: "2026-04-09"
last_modified_by: "mda-pipeline"

owner_role: "Solution Architect"
owner_team: "Mortgage Technology"
reviewers:
  - "Integration Architect"
  - "Loan Processing Manager"

domain: "Mortgage"
subdomain: "Property Appraisal"
mda_layer: "PIM"

agent_type: "rpa"
autonomy_level: "full-auto"
confidence_threshold: 0.99
timeout_seconds: 60
retry_policy: "exponential-backoff"
max_retries: 5

capsule_id: "CAP-PA-NTF-001"
contract_id: "ICT-PA-NTF-001"
contract_ref: "ICT-PA-NTF-001"
predecessor_ids:
  - "INT-PA-ASV-001"
successor_ids: []

preconditions:
  - "The LTV determination is Within_LTV."
  - "The appraised value and LTV ratio are recorded in the LOS."
postconditions:
  - "An Appraisal Complete event has been published to the event bus."
  - "The borrower appraisal delivery workflow has been triggered."
  - "The LOS appraisal status is set to Complete."
invariants:
  - "The event payload matches the LOS data exactly; no value modifications."
  - "The borrower delivery trigger is never skipped."
success_criteria:
  - "Event published within 30 seconds of task initiation."
  - "Borrower delivery triggered within 60 seconds."

execution_hints:
  preferred_agent: "property-appraisal-agent"
  tool_access: []
  forbidden_actions:
    - "browser_automation"
    - "screen_scraping"
    - "ui_click"
    - "rpa_style_macros"

gaps: []
---

# Publish Appraisal Completion Event

## Outcome Statement

When this intent is fulfilled, all downstream systems and stakeholders have been notified that the appraisal is finalized, the borrower delivery process has been initiated, and the loan is cleared to proceed. The agent achieves this by publishing a domain event to the enterprise event bus and updating the LOS status.

## Outcome Contract

**Preconditions (GIVEN):**

- The value assessment determined the LTV is within program limits.
- The appraised value and LTV are available in the LOS.

**Postconditions (THEN):**

- The Appraisal Complete event is published.
- The borrower delivery workflow is triggered.
- The LOS status reflects completion.

**Invariants (ALWAYS):**

- The event payload is consistent with the LOS data.
- Borrower delivery is always triggered regardless of other event delivery status.

## Reasoning Guidance

1. **Assess inputs** -- Verify the LTV determination and appraised value.
2. **Build event payload** -- Assemble the completion event with loan number, appraised value, LTV, and effective date.
3. **Publish event** -- Send to the enterprise event bus.
4. **Trigger borrower delivery** -- Initiate the disclosure system workflow.
5. **Update LOS** -- Set appraisal status to Complete.
6. **Check rate lock** -- Compare lock expiration with completion date and flag if needed.
7. **Validate postconditions** -- Confirm event published, delivery triggered, and status updated.

## Anti-Patterns

The agent MUST NOT:

- **Generate, suggest, or assume any user-interface element** -- no HTML, CSS, or UI references.
- **Modify the appraised value or LTV** -- the event must reflect the assessed data exactly.
- **Skip the borrower delivery trigger** -- ECOA requires timely delivery of the appraisal report.
- **Swallow event bus failures silently** -- failures must be logged and retried.
- **Publish incomplete events** -- all required fields must be present in the payload.

## Paired Capsule

| Field | Value |
|-------|-------|
| Capsule ID | `CAP-PA-NTF-001` |
| Capsule Name | Emit Appraisal Complete Event |
| Location | `triples/emit-complete/emit-complete.cap.md` |

## Paired Integration Contract

| Field | Value |
|-------|-------|
| Contract ID | `ICT-PA-NTF-001` |
| Contract Name | Emit Appraisal Complete Binding |
| Location | `triples/emit-complete/emit-complete.contract.md` |
