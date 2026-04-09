---
intent_id: "INT-PA-REV-001"
intent_name: "Compose and Transmit Appraisal Revision Request"
bpmn_task_id: "Task_RequestRevision"
bpmn_task_name: "Request Appraisal Revision"
process_id: "Process_PropertyAppraisal"
process_name: "Property Appraisal"
goal: "Submit appraisal revision request to AMC for identified deficiencies"
goal_type: "notification"

version: "1.0.0"
status: "draft"

generated_from: "CAP-PA-REV-001"
generated_date: "2026-04-09"
generated_by: "mda-pipeline"
last_modified: "2026-04-09"
last_modified_by: "mda-pipeline"

owner_role: "Solution Architect"
owner_team: "Mortgage Technology"
reviewers:
  - "Chief Appraiser"
  - "Compliance Officer"

domain: "Mortgage"
subdomain: "Property Appraisal"
mda_layer: "PIM"

agent_type: "llm"
autonomy_level: "human-confirm"
confidence_threshold: 0.95
timeout_seconds: 120
retry_policy: "exponential-backoff"
max_retries: 3

capsule_id: "CAP-PA-REV-001"
contract_id: "ICT-PA-REV-001"
contract_ref: "ICT-PA-REV-001"
predecessor_ids:
  - "INT-PA-VAL-001"
successor_ids:
  - "INT-PA-RCV-001"

preconditions:
  - "The completeness validation has produced at least one deficiency code."
  - "The current revision count for this engagement is less than 2."
postconditions:
  - "A revision request has been transmitted to the AMC identifying all deficiency codes."
  - "The LOS status is updated to Revision Requested."
  - "The communication audit trail contains the full text of the request."
invariants:
  - "The revision request contains no language suggesting or requiring a specific appraised value."
  - "Only the appraisal desk identity is used as the sender; loan officer identity is never disclosed."
success_criteria:
  - "Revision request transmitted to AMC within 2 minutes of composition."
  - "Zero value-influencing language detected by the compliance filter."

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

# Compose and Transmit Appraisal Revision Request

## Outcome Statement

When this intent is fulfilled, a compliant revision request has been sent to the AMC detailing the specific deficiencies found during completeness validation, the loan status reflects the pending revision, and the communication is logged for regulatory audit. The agent achieves this by mapping deficiency codes to descriptive narratives and applying a compliance filter before transmission.

## Outcome Contract

**Preconditions (GIVEN):**

- At least one deficiency code exists from the completeness check.
- The engagement has not exceeded the maximum revision count.

**Postconditions (THEN):**

- The revision request has been transmitted to the AMC.
- All deficiency codes are included in the request.
- The LOS status and audit trail are updated.

**Invariants (ALWAYS):**

- No value-influencing language appears in the request.
- The sender identity is the appraisal desk, not the loan officer.

## Reasoning Guidance

1. **Assess inputs** -- Verify deficiency codes and revision count.
2. **Map deficiency codes** -- Convert each code to a clear, factual description of the missing item.
3. **Compose message** -- Build the revision request with order ID, deficiency descriptions, and requested turnaround.
4. **Apply compliance filter** -- Scan the composed message for value-influencing language patterns.
5. **Request human confirmation** -- Present the composed message to the appraisal desk for approval before sending.
6. **Transmit** -- Send the approved message via the Appraisal Portal.
7. **Update records** -- Write the status and audit trail entries.

## Anti-Patterns

The agent MUST NOT:

- **Generate, suggest, or assume any user-interface element** -- no HTML, CSS, or UI references.
- **Include value opinions or suggestions** -- never reference the loan amount, LTV target, or desired value.
- **Bypass the compliance filter** -- the filter must run before every transmission.
- **Send the request without human confirmation** -- the autonomy level requires appraisal desk approval.
- **Exceed the maximum revision count** -- block and escalate instead.
- **Disclose borrower financial details** to the appraiser in the revision request.

## Paired Capsule

| Field | Value |
|-------|-------|
| Capsule ID | `CAP-PA-REV-001` |
| Capsule Name | Request Appraisal Revision |
| Location | `triples/request-revision/request-revision.cap.md` |

## Paired Integration Contract

| Field | Value |
|-------|-------|
| Contract ID | `ICT-PA-REV-001` |
| Contract Name | Request Appraisal Revision Binding |
| Location | `triples/request-revision/request-revision.contract.md` |
